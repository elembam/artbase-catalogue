"""
artbase_export/writers/json_writer.py

Writes canonical models to data/ as JSON files.
Tracks which files changed so the Git handler can commit them.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Union

from artbase_export.canonical.models import CanonicalArtist, CanonicalArtwork

logger = logging.getLogger(__name__)

CanonicalEntity = Union[CanonicalArtist, CanonicalArtwork]


def _entity_dir(entity: CanonicalEntity, output_dir: Path) -> Path:
    if isinstance(entity, CanonicalArtist):
        return output_dir / "artists"
    return output_dir / "artworks"


def _file_path(entity: CanonicalEntity, output_dir: Path) -> Path:
    d = _entity_dir(entity, output_dir)
    return d / f"{entity.artbase_id}.json"


def _serialize(entity: CanonicalEntity) -> str:
    """Serialize a canonical model to a pretty-printed JSON string."""
    # Use model_dump to include private fields with the _schema prefix
    data = entity.model_dump(mode="json", by_alias=True)

    # Inject the schema type — it's a ClassVar in the model, not an instance field
    schema_value = getattr(entity, "_schema", "artbase:unknown:v1")
    data["_schema"] = schema_value

    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False)


def write_entity(entity: CanonicalEntity, output_dir: Path) -> tuple[Path, bool]:
    """
    Write an entity to its canonical JSON file.

    Returns: (path, changed)
      changed=True  → file was created or its content changed
      changed=False → file already existed with identical content
    """
    path = _file_path(entity, output_dir)
    path.parent.mkdir(parents=True, exist_ok=True)

    new_content = _serialize(entity)
    new_hash    = hashlib.sha256(new_content.encode()).hexdigest()

    # Check whether the existing file has the same content
    if path.exists():
        old_content = path.read_text(encoding="utf-8")
        old_hash    = hashlib.sha256(old_content.encode()).hexdigest()
        if old_hash == new_hash:
            return path, False   # unchanged

    path.write_text(new_content, encoding="utf-8")
    return path, True


def write_entities(
    entities: list[CanonicalEntity],
    output_dir: Path,
) -> dict[str, list[Path]]:
    """
    Write a list of entities. Returns {"created": [...], "updated": [...], "unchanged": [...]}.
    """
    results: dict[str, list[Path]] = {"created": [], "updated": [], "unchanged": []}

    for entity in entities:
        path        = _file_path(entity, output_dir)
        existed     = path.exists()
        p, changed  = write_entity(entity, output_dir)
        if not changed:
            results["unchanged"].append(p)
        elif existed:
            results["updated"].append(p)
        else:
            results["created"].append(p)
        logger.debug(f"{'created' if not existed else 'updated' if changed else 'unchanged'}: {p.name}")

    return results
