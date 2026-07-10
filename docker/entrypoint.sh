#!/bin/sh
# ═══════════════════════════════════════════════════════════════
#  Shogun — modular entrypoint
#
#  Assembles PYTHONPATH from whichever per-module venv volumes are
#  present and populated (/venv_core, /venv_torch, /venv_playwright),
#  then execs the real command. /venv_core is required — the app
#  can't run without fastapi/sqlalchemy/etc; the other two are
#  optional depending on the SHOGUN_TORCH / SHOGUN_PLAYWRIGHT
#  settings used when the init services ran (see docker-compose.yml).
# ═══════════════════════════════════════════════════════════════
set -e

PY_MINOR="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
PYTHONPATH_PARTS=""

add_module() {
    module_dir="$1"
    module_name="$2"
    site_packages="$module_dir/lib/python$PY_MINOR/site-packages"
    if [ -d "$site_packages" ] && [ -n "$(ls -A "$site_packages" 2>/dev/null)" ]; then
        PYTHONPATH_PARTS="${PYTHONPATH_PARTS:+$PYTHONPATH_PARTS:}$site_packages"
        echo "entrypoint: $module_name module found ($site_packages)"
    else
        echo "entrypoint: $module_name module not present, skipping"
    fi
}

add_module /venv_core core
add_module /venv_torch torch
add_module /venv_playwright playwright

if [ -z "$PYTHONPATH_PARTS" ]; then
    echo "ERROR: no venv modules found (checked /venv_core, /venv_torch, /venv_playwright)." >&2
    echo "core-init must complete before this container starts — check 'docker compose" >&2
    echo "logs core-init' and docker-compose.yml's depends_on." >&2
    exit 1
fi

# core is mandatory — the app cannot import fastapi/sqlalchemy without it.
case ":$PYTHONPATH_PARTS:" in
    *:/venv_core/lib/python$PY_MINOR/site-packages:*) ;;
    *)
        echo "ERROR: /venv_core is required but was not found or is empty." >&2
        echo "core-init must run before this container starts." >&2
        exit 1
        ;;
esac

export PYTHONPATH="${PYTHONPATH_PARTS}:/app"

# If playwright-init downloaded browsers into its own volume, point
# Playwright at them instead of the default (~/.cache/ms-playwright,
# which wouldn't persist and wouldn't exist in this slim image anyway).
if [ -d /venv_playwright/browsers ]; then
    export PLAYWRIGHT_BROWSERS_PATH=/venv_playwright/browsers
fi

exec "$@"
