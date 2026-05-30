"""
artbase_export/import_cli.py

Import pipeline: source HTML files → Airtable.

Usage:
    artbase-import lnma                          # import LNMA (dry-run preview)
    artbase-import lnma --execute                # actually write to Airtable
    artbase-import lnma --execute --limit 10     # write first 10 rows only (testing)
    artbase-import swedbank                      # import Hansabanka/Swedbank (dry-run)
    artbase-import swedbank --execute
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app     = typer.Typer(help="Ars Accordia import pipeline — source HTML → Airtable")
console = Console()

# Default HTML paths — resolved relative to the repo root (ArtBase/)
_REPO_ROOT    = Path(__file__).parent.parent.parent.parent
_LNMA_DEFAULT = _REPO_ROOT / "ArsAccordiaClaude" / "lnmm.html"
_SWB_DEFAULT  = _REPO_ROOT / "ArsAccordiaClaude" / "swedbank.html"


# ── Config helper ──────────────────────────────────────────────────────────────

def _load_config(config_path: Path) -> dict:
    import yaml
    if not config_path.exists():
        console.print(f"[red]✗ Config file not found: {config_path}[/]")
        console.print("[dim]Copy config.yaml.example → config.yaml and add credentials.[/]")
        raise typer.Exit(1)
    with open(config_path) as f:
        return yaml.safe_load(f)


# ── Shared import engine ───────────────────────────────────────────────────────

def _run_import(
    source:    str,          # "lnma" | "swb"
    html_path: Path,
    cfg:       dict,
    execute:   bool,         # False = dry-run (default safe mode)
    limit:     int | None,
) -> None:
    """
    Core import logic shared by both commands.

    Sequence:
      1. Parse HTML → rows
      2. Ensure Collection record exists
      3. Upsert artists (skip existing by Display Name)
      4. Create artwork records (skip if Source Record ID already present)
      5. Log an Imports row
    """
    from pyairtable import Api
    from artbase_export.airtable.schema import (
        ArtistFields, ArtworkFields, CollectionFields, ImportFields, Tables,
    )

    if source == "lnma":
        import artbase_export.importer.lnma as src_mod
        artist_name_key = "Creator"
        source_rec_id_key = "Collection Number"
    else:
        import artbase_export.importer.swedbank as src_mod
        artist_name_key = "artist"
        source_rec_id_key = "id"

    api     = Api(cfg["airtable"]["token"])
    base_id = cfg["airtable"]["base_id"]

    artists_table     = api.table(base_id, Tables.ARTISTS)
    artworks_table    = api.table(base_id, Tables.ARTWORKS)
    collections_table = api.table(base_id, Tables.COLLECTIONS)
    imports_table     = api.table(base_id, Tables.IMPORTS)

    dry_tag = "[dim](dry-run)[/] " if not execute else ""

    # ── 1. Parse HTML ──────────────────────────────────────────────────────
    console.print(f"\n[bold]1 / 5  Parsing {html_path.name}[/]")
    rows = src_mod.parse_rows(html_path)
    if limit:
        rows = rows[:limit]
    console.print(f"  {len(rows)} rows loaded{' (limited)' if limit else ''}")

    # ── 2. Collection ──────────────────────────────────────────────────────
    console.print(f"\n[bold]2 / 5  Collection — {src_mod.CLIENT_CODE}[/]")
    existing_cols = collections_table.all(
        formula=f'{{{CollectionFields.CLIENT_CODE}}} = "{src_mod.CLIENT_CODE}"',
    )
    if existing_cols:
        collection_rec_id = existing_cols[0]["id"]
        console.print(f"  [dim]Already exists ({collection_rec_id})[/]")
    elif execute:
        rec = collections_table.create(src_mod.COLLECTION_RECORD)
        collection_rec_id = rec["id"]
        console.print(f"  [green]Created ({collection_rec_id})[/]")
    else:
        console.print(f"  {dry_tag}Would create collection {src_mod.CLIENT_CODE}")
        collection_rec_id = "DRY_RUN_COLLECTION"

    # ── 3. Artists ─────────────────────────────────────────────────────────
    console.print(f"\n[bold]3 / 5  Artists[/]")

    # Collect unique artist names preserving first-seen row (for lifespan)
    seen: dict[str, dict[str, str]] = {}
    for row in rows:
        name = row.get(artist_name_key, "").strip()
        if name and name not in seen:
            seen[name] = row
    console.print(f"  {len(seen)} unique artists in source")

    # Fetch all existing artists once to build a name → rec-id lookup
    console.print("  Fetching existing artists from Airtable…")
    existing_artists = artists_table.all(fields=[ArtistFields.DISPLAY_NAME])
    existing_by_name: dict[str, str] = {
        r["fields"].get(ArtistFields.DISPLAY_NAME, ""): r["id"]
        for r in existing_artists
        if ArtistFields.DISPLAY_NAME in r["fields"]
    }

    artist_id_map: dict[str, str] = {}   # display_name → Airtable record ID
    to_create: list[tuple[str, dict]] = []

    for name, row in seen.items():
        if name in existing_by_name:
            artist_id_map[name] = existing_by_name[name]
        else:
            if source == "lnma":
                fields = src_mod.build_artist_fields(row)
            else:
                fields = src_mod.build_artist_fields(name)
            to_create.append((name, fields))

    skipped_artists = len(seen) - len(to_create)
    console.print(
        f"  {skipped_artists} already in Airtable, "
        f"{len(to_create)} to {'create' if execute else 'create (dry-run)'}"
    )

    if execute and to_create:
        new_recs = artists_table.batch_create([f for _, f in to_create])
        for i, rec in enumerate(new_recs):
            name = to_create[i][0]
            artist_id_map[name] = rec["id"]
        console.print(f"  [green]+{len(new_recs)} artists created[/]")
    elif not execute:
        for name, _ in to_create:
            console.print(f"  {dry_tag}Would create artist: {name}")

    # ── 4. Artworks ────────────────────────────────────────────────────────
    console.print(f"\n[bold]4 / 5  Artworks[/]")

    # Fetch existing source record IDs for this collection to skip duplicates
    console.print("  Fetching existing artwork records for this collection…")
    existing_artworks = artworks_table.all(
        formula=f'{{{ArtworkFields.CLIENT_CODE}}} = "{src_mod.CLIENT_CODE}"',
        fields=[ArtworkFields.SOURCE_RECORD_ID],
    )
    existing_src_ids: set[str] = {
        r["fields"].get(ArtworkFields.SOURCE_RECORD_ID, "")
        for r in existing_artworks
        if ArtworkFields.SOURCE_RECORD_ID in r["fields"]
    }
    console.print(f"  {len(existing_src_ids)} artworks already in Airtable")

    artwork_fields_list: list[dict] = []
    skipped_artworks = 0

    for i, row in enumerate(rows, start=1):
        src_rec_id   = row.get(source_rec_id_key, "").strip()
        artist_name  = row.get(artist_name_key, "").strip()
        passport_id  = f"{src_mod.AA_ID_PREFIX}{i:03d}"
        artist_rec_id = artist_id_map.get(artist_name)

        if src_rec_id in existing_src_ids:
            skipped_artworks += 1
            continue

        fields = src_mod.build_artwork_fields(
            row, artist_rec_id, collection_rec_id, passport_id
        )
        artwork_fields_list.append(fields)

    console.print(
        f"  {skipped_artworks} already imported, "
        f"{len(artwork_fields_list)} to {'create' if execute else 'create (dry-run)'}"
    )

    if execute and artwork_fields_list:
        with console.status(f"  Writing {len(artwork_fields_list)} artworks to Airtable…"):
            artworks_table.batch_create(artwork_fields_list)
        console.print(f"  [green]+{len(artwork_fields_list)} artworks created[/]")
    elif not execute and artwork_fields_list:
        # Show a preview table of the first 5 records
        preview = Table(title="Preview (first 5)", show_lines=True)
        preview.add_column("Passport ID", style="cyan", no_wrap=True)
        preview.add_column("Title")
        preview.add_column("Artist")
        preview.add_column("Date")
        preview.add_column("Medium", overflow="fold")
        for f in artwork_fields_list[:5]:
            preview.add_row(
                f.get(ArtworkFields.PASSPORT_ID, ""),
                f.get(ArtworkFields.WORK_TITLE, ""),
                f.get(ArtworkFields.ARTIST_DISPLAY, ""),
                f.get(ArtworkFields.DATE_DISPLAY, ""),
                f.get(ArtworkFields.MEDIUM_DISPLAY, ""),
            )
        console.print(preview)

    # ── 5. Log import record ───────────────────────────────────────────────
    console.print(f"\n[bold]5 / 5  Import log[/]")
    if execute:
        imports_table.create({
            ImportFields.SOURCE_SYSTEM:   src_mod.SOURCE_SYSTEM,
            ImportFields.CLIENT_CODE:     src_mod.CLIENT_CODE,
            ImportFields.FILE_NAME:       html_path.name,
            ImportFields.EXPORT_DATE:     date.today().isoformat(),
            ImportFields.STATUS:          "completed",
            ImportFields.ROWS_IMPORTED:   str(len(rows)),
            ImportFields.RECORDS_CREATED: str(len(artwork_fields_list)),
            ImportFields.RECORDS_UPDATED: "0",
            ImportFields.OPERATOR:        "artbase-import",
        })
        console.print("  [green]Import record created[/]")
    else:
        console.print(f"  {dry_tag}Would log import record")

    # ── Summary ────────────────────────────────────────────────────────────
    console.rule()
    console.print(
        f"{dry_tag}"
        f"[green]+{len(artwork_fields_list)} artworks[/]  "
        f"[green]+{len(to_create)} artists[/]  "
        f"[dim]={skipped_artworks + skipped_artists} skipped[/]"
    )
    if not execute:
        console.print(
            "[yellow]Dry-run complete — nothing was written. "
            "Add --execute to import.[/]"
        )


# ── CLI commands ───────────────────────────────────────────────────────────────

@app.command()
def lnma(
    config:  Path          = typer.Option(Path("config.yaml"), help="Path to config.yaml"),
    html:    Path          = typer.Option(_LNMA_DEFAULT,       help="Path to lnmm.html"),
    execute: bool          = typer.Option(False, "--execute",  help="Write to Airtable (default: dry-run)"),
    limit:   Optional[int] = typer.Option(None,  "--limit",    help="Import only first N rows (testing)"),
    verbose: bool          = typer.Option(False, "--verbose", "-v"),
):
    """
    Import LNMA artworks and artists from lnmm.html into Airtable.

    Runs as a dry-run by default — pass --execute to write.
    """
    logging.basicConfig(level=logging.DEBUG if verbose else logging.WARNING)
    if not html.exists():
        console.print(f"[red]✗ HTML file not found: {html}[/]")
        raise typer.Exit(1)
    cfg = _load_config(config)
    _run_import("lnma", html, cfg, execute, limit)


@app.command()
def swedbank(
    config:  Path          = typer.Option(Path("config.yaml"), help="Path to config.yaml"),
    html:    Path          = typer.Option(_SWB_DEFAULT,        help="Path to swedbank.html"),
    execute: bool          = typer.Option(False, "--execute",  help="Write to Airtable (default: dry-run)"),
    limit:   Optional[int] = typer.Option(None,  "--limit",    help="Import only first N rows (testing)"),
    verbose: bool          = typer.Option(False, "--verbose", "-v"),
):
    """
    Import Hansabanka / Swedbank artworks and artists from swedbank.html into Airtable.

    Runs as a dry-run by default — pass --execute to write.
    """
    logging.basicConfig(level=logging.DEBUG if verbose else logging.WARNING)
    if not html.exists():
        console.print(f"[red]✗ HTML file not found: {html}[/]")
        raise typer.Exit(1)
    cfg = _load_config(config)
    _run_import("swb", html, cfg, execute, limit)


if __name__ == "__main__":
    app()
