# Docker Runbook — Shogun + Gensui

Operational guide for running Shogun (Tenshu) and Gensui (fleet management)
via Docker. Covers the containers this POC built, tested, and fixed —
not the venv-based `install.sh` path, which is documented in the main
[README.md](../README.md).

## Prerequisites

- Docker Engine with the `compose` plugin (`docker compose version`)
- No prior install required — both images build from source

## Directory layout

```text
docker/docker-compose.yml   # centralized compose: shogun + gensui + optional nginx
Dockerfile                  # Shogun (Tenshu) image — build context: repo root
gensui/Dockerfile           # Gensui image — build context: repo root (not gensui/, see below)
gensui/.env                 # Gensui config (copy from gensui/.env.example)
```

`docker/docker-compose.yml` is the single entry point for both services.
Both Dockerfiles stay at their original locations — repo root and
`gensui/` — because their `COPY` instructions are relative to those
paths. Do not move a Dockerfile without re-checking every `COPY` line;
see "History: path bugs fixed" below for what happens when this goes
wrong.

## First-time setup

```bash
# Gensui needs an .env file — Shogun does not (auto-generated on first run)
cp gensui/.env.example gensui/.env
# Edit gensui/.env: set GENSUI_JWT_SECRET to a random 64-char string
#   openssl rand -base64 48 | tr -d '\n=+/'

cd docker
docker compose up -d --build
```

First build takes several minutes — Shogun's image installs `torch`,
`transformers`, and Playwright's Chromium; Gensui's is lighter.

## Verify

```bash
curl -s http://127.0.0.1:8000/api/v1/health   # Shogun
curl -s http://127.0.0.1:8787/api/gensui/health  # Gensui
```

Both should return `{"status":"ok",...}`. Web UIs:

- Shogun setup wizard: `http://127.0.0.1:8000/setup`
- Gensui admin (default login `admin@gensui.local` / `changeme` — change
  immediately): `http://127.0.0.1:8787`

Neither binds to `0.0.0.0` — both are `127.0.0.1`-only. Remote access
goes through an SSH tunnel:

```bash
ssh -L 8000:127.0.0.1:8000 -L 8787:127.0.0.1:8787 <your-ssh-alias>
```

## Common operations

```bash
cd docker

docker compose ps                       # status of both services
docker compose logs -f shogun           # follow Shogun logs
docker compose logs -f gensui           # follow Gensui logs
docker compose restart shogun           # restart one service
docker compose up -d --build shogun     # rebuild + restart one service
docker compose down                     # stop both (keeps volumes/data)
docker compose --profile server up -d   # also start the Gensui nginx/TLS proxy
```

## Data persistence

Named Docker volumes, one set per service — nothing is stored in
bind-mounted host directories:

- **Shogun**: `repo_shogun_data`, `repo_shogun_logs`, `repo_shogun_configs`,
  `repo_shogun_vault`
- **Gensui**: `gensui_gensui_data`, `gensui_gensui_logs`

These predate `docker/docker-compose.yml` (created by the original
per-service compose files during this POC) and are referenced as
`external: true` in the centralized compose file specifically so that
moving to this file does not create fresh, empty volumes or orphan
existing data. If you're setting this up from scratch (no prior
volumes exist), Compose creates them automatically on first
`docker compose up` — `external: true` only matters for *reusing*
existing ones; it doesn't require them to pre-exist by hand.

## Known non-blocking issue

Qdrant (vector memory / RAG) shows **OFFLINE** in the Shogun UI
(Operations tab) even though the app itself is healthy. Not
investigated further in this POC — likely a `QDRANT_PATH` resolution
issue inside the container. Does not block normal use of the UI or
API.

## Troubleshooting

### Container crash-loops on startup, `ModuleNotFoundError`

Rebuild with `--build` — a stale image layer is the usual cause after
a `pyproject.toml` change: `docker compose up -d --build <service>`.

### `GET /` returns `{"detail":"Not Found"}`

Historically caused by two separate bugs in Gensui (see below) —
should not recur if you're building from this repo's current state.
If it does, check `docker exec gensui-afm ls /app/frontend/dist/` — if
that's empty, the frontend build stage failed silently; check
`docker compose logs gensui` for `npm` errors during build.

### UI loads but every API call 404s

Compare the API prefix the browser is calling (Network tab) against
what the backend actually serves (`/api/gensui/*` for Gensui,
`/api/v1/*` for Shogun). If they don't match, the wrong frontend was
built into the image — see the Dockerfile fix in the history below.

### `attempt to write a readonly database` on Gensui startup

The `gensui_gensui_data` volume was created by an older, root-owned
container and the current image runs as a non-root user (uid 1000).
Fix:

```bash
docker run --rm -v gensui_gensui_data:/data alpine chown -R 1000:1000 /data
docker run --rm -v gensui_gensui_logs:/logs alpine chown -R 1000:1000 /logs
```

## History: path bugs fixed during this POC

For context on why the Dockerfiles look the way they do, and why
build contexts are anchored at the repo root rather than each
service's subdirectory — nine real bugs were found and fixed getting
Shogun and Gensui's Docker install to actually work, plus a
security/dependency pass. Full detail and reproduction steps in the
corresponding upstream issues:

- [AlphaHorizon-AI/Shogun#3](https://github.com/AlphaHorizon-AI/Shogun/issues/3) — `bcrypt`/`pyjwt` missing from `pyproject.toml`, container crash-loops on boot
- [AlphaHorizon-AI/Shogun#4](https://github.com/AlphaHorizon-AI/Shogun/issues/4) — `gensui/docker-compose.yml` referenced in docs but never committed
- [AlphaHorizon-AI/Shogun#5](https://github.com/AlphaHorizon-AI/Shogun/issues/5) — frontend dist path resolution bug, root route always 404s
- [AlphaHorizon-AI/Shogun#6](https://github.com/AlphaHorizon-AI/Shogun/issues/6) — Dockerfile built the wrong frontend (main Shogun UI instead of Gensui admin UI) depending on build context
- [AlphaHorizon-AI/Shogun#7](https://github.com/AlphaHorizon-AI/Shogun/issues/7) — 31 dependency vulnerabilities (axios, react-router-dom, form-data, vite)
- [AlphaHorizon-AI/Shogun#8](https://github.com/AlphaHorizon-AI/Shogun/issues/8) — stored XSS in Kaizen mandate preview
- [AlphaHorizon-AI/Shogun#9](https://github.com/AlphaHorizon-AI/Shogun/issues/9) — SSRF in A2A peer invitation and Gensui connect endpoints
- [AlphaHorizon-AI/Shogun#10](https://github.com/AlphaHorizon-AI/Shogun/issues/10) — Gensui container ran as root
- [AlphaHorizon-AI/Shogun#11](https://github.com/AlphaHorizon-AI/Shogun/issues/11) — no Dockerfile existed yet for the main Shogun app

All fixed and available as tested PRs against upstream (#12–#20).
