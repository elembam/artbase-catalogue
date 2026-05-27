"""
artbase_export/cli.py

Command-line interface.

Usage:
    artbase-export run                     # export everything
    artbase-export run --artist ART-HERBERTS-SILINS-1926
    artbase-export run --dry-run
    artbase-export validate
    artbase-export status
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

app     = typer.Typer(help="ArtBase export pipeline — Airtable → canonical JSON")
console = Console()


# ── Config loading ─────────────────────────────────────────────────────────────

def _load_config(config_path: Path) -> dict:
    import yaml
    if not config_path.exists():
        console.print(f"[red]✗ Config file not found: {config_path}[/]")
        console.print("[dim]Copy config.yaml.example to config.yaml and fill in credentials.[/]")
        raise typer.Exit(1)
    with open(config_path) as f:
        return yaml.safe_load(f)


# ── Commands ───────────────────────────────────────────────────────────────────

@app.command()
def run(
    config:     Path            = typer.Option(Path("config.yaml"), help="Path to config.yaml"),
    artist:     Optional[str]   = typer.Option(None,  help="Export a single artist by ID"),
    artwork:    Optional[str]   = typer.Option(None,  help="Export a single artwork by ID"),
    dry_run:    bool            = typer.Option(False, "--dry-run", help="Preview changes without writing"),
    verbose:    bool            = typer.Option(False, "--verbose", "-v"),
):
    """Export Airtable records to canonical JSON files and commit to Git."""

    logging.basicConfig(
        level   = logging.DEBUG if verbose else logging.INFO,
        format  = "%(levelname)s  %(message)s",
    )

    cfg     = _load_config(config)
    output  = Path(cfg["export"]["output_dir"])

    from artbase_export.airtable.client import AirtableClient
    from artbase_export.transform.artist import transform_artist
    from artbase_export.writers.json_writer import write_entities
    from artbase_export.writers.git_handler import GitHandler

    client = AirtableClient(
        token       = cfg["airtable"]["token"],
        base_id     = cfg["airtable"]["base_id"],
        table_names = cfg["airtable"].get("tables", {}),
    )

    all_changed: list[Path] = []
    stats = {"created": 0, "updated": 0, "unchanged": 0, "errors": 0}

    # ── Artists ────────────────────────────────────────────────────────────
    with console.status("[bold]Fetching artists from Airtable…[/]"):
        raw_artists = list(client.iter_artists(artist_id=artist))
    console.print(f"[dim]Fetched {len(raw_artists)} artist(s)[/]")

    canonical_artists = []
    for raw in raw_artists:
        artist_id = raw.get("Artist ID", "UNKNOWN")
        try:
            canonical = transform_artist(raw)
            canonical_artists.append(canonical)
        except Exception as e:
            console.print(f"[red]✗ Artist {artist_id}: {e}[/]")
            stats["errors"] += 1

    if not dry_run:
        results = write_entities(canonical_artists, output)
        for created_path in results["created"]:
            console.print(f"[green]+ {created_path.name}[/]")
            stats["created"] += 1
        for updated_path in results["updated"]:
            console.print(f"[yellow]~ {updated_path.name}[/]")
            stats["updated"] += 1
        stats["unchanged"] += len(results["unchanged"])
        all_changed.extend(results["created"] + results["updated"])
    else:
        for c in canonical_artists:
            console.print(f"[dim]  (dry-run) would write {c.artbase_id}.json[/]")

    # ── Artworks ───────────────────────────────────────────────────────────
    if not artist:  # skip artworks if filtering to a single artist
        with console.status("[bold]Fetching artworks from Airtable…[/]"):
            raw_artworks = list(client.iter_artworks(artwork_id=artwork))
        console.print(f"[dim]Fetched {len(raw_artworks)} artwork(s)[/]")

        from artbase_export.transform.artwork import transform_artwork
        canonical_artworks = []
        for raw in raw_artworks:
            artwork_id = raw.get("Artwork ID", "UNKNOWN")
            try:
                canonical = transform_artwork(raw)
                canonical_artworks.append(canonical)
            except Exception as e:
                console.print(f"[red]✗ Artwork {artwork_id}: {e}[/]")
                stats["errors"] += 1

        if not dry_run:
            results = write_entities(canonical_artworks, output)
            for p in results["created"]:
                console.print(f"[green]+ {p.name}[/]")
                stats["created"] += 1
            for p in results["updated"]:
                console.print(f"[yellow]~ {p.name}[/]")
                stats["updated"] += 1
            stats["unchanged"] += len(results["unchanged"])
            all_changed.extend(results["created"] + results["updated"])

    # ── Git commit ─────────────────────────────────────────────────────────
    if not dry_run and all_changed and cfg["export"].get("auto_commit", True):
        try:
            git = GitHandler(
                repo_root       = output.parent,
                author_name     = cfg["export"].get("git_author_name", "ArtBase Export"),
                author_email    = cfg["export"].get("git_author_email", "export@artbase.eu"),
            )
            details = _build_commit_details(stats, all_changed)
            sha = git.commit_changes(
                all_changed,
                summary = f"Export {_now_iso()}",
                details = details,
            )
            if sha:
                console.print(f"[dim]Git commit: {sha[:8]}[/]")
        except RuntimeError as e:
            console.print(f"[yellow]⚠ Git not available: {e}[/]")

    # ── Summary ────────────────────────────────────────────────────────────
    _print_summary(stats, dry_run)

    if stats["errors"] > 0:
        raise typer.Exit(1)


@app.command()
def validate(
    config:     Path = typer.Option(Path("config.yaml")),
    output_dir: Optional[Path] = typer.Option(None),
):
    """Validate existing canonical JSON files without touching Airtable."""
    import json
    from artbase_export.canonical.models import CanonicalArtist, CanonicalArtwork

    if output_dir is None:
        cfg      = _load_config(config)
        data_dir = Path(cfg["export"]["output_dir"])
    else:
        data_dir = output_dir

    errors = 0
    ok     = 0

    for json_file in sorted(data_dir.rglob("*.json")):
        try:
            raw = json.loads(json_file.read_text(encoding="utf-8"))
            schema = raw.get("_schema", "")
            if "artist" in schema:
                CanonicalArtist.model_validate(raw)
            elif "artwork" in schema:
                CanonicalArtwork.model_validate(raw)
            ok += 1
        except Exception as e:
            console.print(f"[red]✗ {json_file.name}: {e}[/]")
            errors += 1

    console.print(f"\n{'✓' if errors == 0 else '✗'} {ok} valid, {errors} invalid")
    if errors > 0:
        raise typer.Exit(1)


@app.command()
def status(
    config:     Path = typer.Option(Path("config.yaml")),
    output_dir: Optional[Path] = typer.Option(None),
):
    """Show a status table of all canonical records."""
    import json
    from artbase_export.canonical.models import CanonicalArtist, CanonicalArtwork

    if output_dir is None:
        cfg      = _load_config(config)
        data_dir = Path(cfg["export"]["output_dir"])
    else:
        data_dir = output_dir

    table = Table(title="ArtBase Canonical Records")
    table.add_column("ID",          style="cyan",  no_wrap=True)
    table.add_column("Type",        style="dim")
    table.add_column("Name")
    table.add_column("Status",      style="yellow")
    table.add_column("ObjID",       style="green")
    table.add_column("Authorities", style="blue")
    table.add_column("Conflicts",   style="red")

    for json_file in sorted(data_dir.rglob("*.json")):
        try:
            raw     = json.loads(json_file.read_text(encoding="utf-8"))
            schema  = raw.get("_schema", "")

            if "artist" in schema:
                entity  = CanonicalArtist.model_validate(raw)
                name    = entity.identity.preferred_name
                typ     = "artist"
                obj_id  = f"{entity.object_id_score()}/9"
                auths   = _count_confirmed_authorities(entity.authority_links)
                conflicts = str(len(entity.conflicts))
                status_val = entity.cataloguing.review_status.value
            elif "artwork" in schema:
                entity  = CanonicalArtwork.model_validate(raw)
                name    = entity.object_id.title or "(untitled)"
                typ     = "artwork"
                obj_id  = f"{entity.object_id.score()}/9"
                auths   = "-"
                conflicts = str(len(entity.conflicts))
                status_val = entity.cataloguing.review_status.value
            else:
                continue

            table.add_row(entity.artbase_id, typ, name, status_val,
                          obj_id, auths, conflicts)
        except Exception as e:
            table.add_row(json_file.stem, "?", f"[red]{e}[/]", "-", "-", "-", "-")

    console.print(table)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _count_confirmed_authorities(links) -> str:
    confirmed = sum(
        1 for field in ["wikidata", "viaf", "ulan", "isni", "rkd", "lc_naco", "gnd", "bnf"]
        if getattr(links, field, None) and
           getattr(links, field).status.value == "confirmed"
    )
    return f"{confirmed}/8"


def _build_commit_details(stats: dict, changed: list[Path]) -> str:
    lines = [
        f"Created: {stats['created']}  Updated: {stats['updated']}  Unchanged: {stats['unchanged']}",
        "",
    ]
    for p in sorted(changed, key=lambda x: x.name)[:20]:
        lines.append(f"  {p.parent.name}/{p.name}")
    if len(changed) > 20:
        lines.append(f"  … and {len(changed) - 20} more")
    return "\n".join(lines)


def _print_summary(stats: dict, dry_run: bool) -> None:
    mode = "[dim](dry-run)[/]" if dry_run else ""
    console.print(
        f"\n{mode} "
        f"[green]+{stats['created']} created[/]  "
        f"[yellow]~{stats['updated']} updated[/]  "
        f"[dim]={stats['unchanged']} unchanged[/]  "
        + (f"[red]✗{stats['errors']} errors[/]" if stats["errors"] else "")
    )


if __name__ == "__main__":
    app()
