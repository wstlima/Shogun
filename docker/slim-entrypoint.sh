#!/bin/sh
# ═══════════════════════════════════════════════════════════════
#  Shogun (slim variant) — entrypoint
#
#  Activates the venv installed by the torch-init service into
#  /venv (a volume shared with this container), then execs the
#  real command. If /venv/bin/python doesn't exist yet, torch-init
#  hasn't finished — this container should have `depends_on:
#  torch-init: {condition: service_completed_successfully}` in
#  compose so that's not normally reachable, but fail loudly if it
#  somehow is.
# ═══════════════════════════════════════════════════════════════
set -e

if [ ! -x /venv/bin/python ]; then
    echo "ERROR: /venv/bin/python not found. The torch-init service must" >&2
    echo "complete before this container starts — check 'docker compose" >&2
    echo "logs torch-init' and docker-compose.slim.yml's depends_on." >&2
    exit 1
fi

export PATH="/venv/bin:$PATH"
export PYTHONPATH="/app:$PYTHONPATH"

exec "$@"
