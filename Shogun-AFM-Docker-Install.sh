#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
#  SHOGUN AFM — Docker Installer (Linux / macOS)
#
#  Thin shim: runs installer/install.mjs inside an ephemeral
#  node:20-alpine container, so the host only ever needs Docker —
#  no Node.js install required. See installer/install.mjs for the
#  actual logic (all the real logic lives there, not duplicated
#  between .sh and .bat).
#
#  This script never runs `docker compose` — it only prepares
#  config and prints the exact command for you to review and run.
#
#  Usage:
#    Shogun-AFM-Docker-Install.sh [--clean | --image[=TAG]] [--profile server]
#    Shogun-AFM-Docker-Install.sh --help
# ═══════════════════════════════════════════════════════════════

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v docker &>/dev/null; then
    echo "Docker is not installed. See: https://docs.docker.com/get-docker/"
    exit 1
fi

RUN_TTY_FLAGS="-i"
[ -t 0 ] && [ -t 1 ] && RUN_TTY_FLAGS="-it"

docker run --rm $RUN_TTY_FLAGS \
    -v "$SCRIPT_DIR:/repo" \
    -w /repo/installer \
    node:20-alpine \
    sh -c "npm ci --silent --no-progress && node install.mjs $*"
