from __future__ import annotations

import sys
from pathlib import Path

from flask import current_app

_util = None


def _import_util():
    """Import shared ML utilities from the existing server package."""
    global _util
    if _util is not None:
        return _util

    server_dir = Path(current_app.config["SERVER_DIR"])
    server_path = str(server_dir.resolve())
    if server_path not in sys.path:
        sys.path.insert(0, server_path)

    import util  # noqa: WPS433 — runtime import from sibling server/

    _util = util
    return util


def get_util():
    return _import_util()


def ensure_artifacts_loaded() -> None:
    util = get_util()
    if not current_app.config.get("ARTIFACTS_LOADED"):
        util.load_saved_artifacts()
        current_app.config["ARTIFACTS_LOADED"] = True
