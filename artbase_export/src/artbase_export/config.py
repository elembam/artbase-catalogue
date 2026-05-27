"""
artbase_export/config.py

Loads and validates config.yaml.
Provides typed access to all settings.
"""

from __future__ import annotations
from pathlib import Path
import yaml


class AirtableConfig:
    def __init__(self, d: dict):
        self.token      = d.get("token", "")
        self.base_id    = d.get("base_id", "")
        self.tables     = d.get("tables", {})

    def validate(self):
        if not self.token or self.token.startswith("patXXXX"):
            raise ValueError(
                "Airtable token not set.\n"
                "  Edit config.yaml and add your Personal Access Token.\n"
                "  Get one at: https://airtable.com/account"
            )
        if not self.base_id or self.base_id.startswith("appXXXX"):
            raise ValueError(
                "Airtable base_id not set.\n"
                "  Edit config.yaml and add your base ID.\n"
                "  Find it in your Airtable base URL: airtable.com/appXXXXXXXX/..."
            )


class ExportConfig:
    def __init__(self, d: dict):
        self.output_dir     = d.get("output_dir", "./data")
        self.auto_commit    = d.get("auto_commit", True)
        self.git_author_name  = d.get("git_author_name", "ArtBase Export")
        self.git_author_email = d.get("git_author_email", "export@artbase.eu")
        self.min_status     = d.get("min_status", "")


class Config:
    def __init__(self, path: Path):
        if not path.exists():
            raise FileNotFoundError(
                f"Config file not found: {path}\n"
                f"  Run: cp config.yaml.example config.yaml\n"
                f"  Then edit config.yaml with your Airtable credentials."
            )
        with open(path) as f:
            raw = yaml.safe_load(f)

        self.airtable   = AirtableConfig(raw.get("airtable", {}))
        self.export     = ExportConfig(raw.get("export", {}))
        self.log_level  = raw.get("logging", {}).get("level", "INFO")

    def validate(self):
        self.airtable.validate()
