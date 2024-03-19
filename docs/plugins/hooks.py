from __future__ import annotations

import logging
from pathlib import Path

from mkdocs.config import Config


logger = logging.getLogger("mkdocs.plugin")

ROOT_DIR = Path(__file__).parents[2]
DOCS_DIR = Path(__file__).parents[1]


def _add_tracked_file(file: Path, new_file: Path):
    text = file.read_text(encoding="utf-8")

    # avoid writing file unless the content has changed to avoid infinite build loop
    if not new_file.is_file() or new_file.read_text(encoding="utf-8") != text:
        new_file.write_text(text, encoding="utf-8")


def on_pre_build(config: Config):
    _add_tracked_file(ROOT_DIR / "CONTRIBUTING.md", DOCS_DIR / "contributing.md")
    _add_tracked_file(ROOT_DIR / "LICENSE.md", DOCS_DIR / "license.md")
