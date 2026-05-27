"""
artbase_export/writers/git_handler.py

Commits changed canonical files to the Git repository.
Each export run that produces changes is one commit.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

try:
    from git import Repo, InvalidGitRepositoryError, Actor
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

logger = logging.getLogger(__name__)


class GitHandler:
    """
    Manages Git commits for the canonical data/ directory.

    Usage:
        handler = GitHandler(repo_root=Path("."), author_name="ArtBase Export", ...)
        handler.commit_changes(changed_paths, summary="Export 2026-05-27")
    """

    def __init__(
        self,
        repo_root:      Path,
        author_name:    str = "ArtBase Export",
        author_email:   str = "export@artbase.eu",
    ):
        if not GIT_AVAILABLE:
            raise RuntimeError(
                "gitpython is not installed. "
                "Run: pip install gitpython"
            )
        try:
            self._repo = Repo(repo_root, search_parent_directories=True)
        except InvalidGitRepositoryError:
            raise RuntimeError(
                f"No Git repository found at or above {repo_root}. "
                "Run: git init"
            )
        self._author = Actor(author_name, author_email)

    def commit_changes(
        self,
        changed_paths:  list[Path],
        summary:        str,
        details:        str | None = None,
    ) -> str | None:
        """
        Stage and commit changed files.

        Returns the commit SHA if a commit was made; None if nothing changed.
        """
        if not changed_paths:
            logger.info("No changed files to commit")
            return None

        # Stage all changed paths (convert to strings relative to repo root)
        repo_root = Path(self._repo.working_dir)
        relative  = [str(p.relative_to(repo_root)) for p in changed_paths]

        self._repo.index.add(relative)

        # Check if there's actually anything staged
        if not self._repo.index.diff("HEAD") and not self._repo.untracked_files:
            logger.info("Nothing to commit (files staged but diff is empty)")
            return None

        # Build commit message
        ts          = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        message     = f"{summary}\n\n{ts}"
        if details:
            message += f"\n\n{details}"

        commit = self._repo.index.commit(
            message,
            author      = self._author,
            committer   = self._author,
        )
        logger.info(f"Committed {len(changed_paths)} file(s): {commit.hexsha[:8]}")
        return commit.hexsha

    def current_sha(self) -> str | None:
        """Return the current HEAD commit SHA, or None if no commits yet."""
        try:
            return self._repo.head.commit.hexsha
        except Exception:
            return None

    def is_dirty(self) -> bool:
        """True if there are uncommitted changes in the repo."""
        return self._repo.is_dirty(untracked_files=True)
