"""Gensui entry point — run with `python -m gensui`."""

from __future__ import annotations

import uvicorn

from gensui.config import gensui_settings


def main() -> None:
    """Launch the Gensui server."""
    uvicorn.run(
        "gensui.app:create_app",
        factory=True,
        host=gensui_settings.gensui_server_host,
        port=gensui_settings.gensui_server_port,
        reload=gensui_settings.debug,
        log_level="debug" if gensui_settings.debug else "info",
    )


if __name__ == "__main__":
    main()
