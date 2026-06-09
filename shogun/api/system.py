import uuid
from typing import Any
from shogun.engine.vector_store import get_vector_store

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from shogun.config import settings, PROJECT_ROOT
from shogun.schemas.common import ApiResponse
from shogun.api.deps import (
    get_agent_service, 
    get_mission_service, 
    get_security_service
)
from shogun.services.agent_service import AgentService
from shogun.services.mission_service import MissionService
from shogun.services.security_service import SecurityService
from shogun.db.models.agent import Agent
from shogun.db.models.mission import Mission

router = APIRouter(prefix="/system", tags=["System"])


async def _check_qdrant() -> str:
    """Helper to check Qdrant connectivity via the global VectorStore."""
    try:
        store = get_vector_store()
        # Just check if we can get collections from the existing client
        store.client.get_collections()
        return "healthy"
    except Exception:
        return "offline"


@router.get("/health", response_model=ApiResponse)
async def get_system_health():
    """Return system health status for all components."""
    qdrant_status = await _check_qdrant()
    
    return ApiResponse(
        success=True,
        data={
            "runtime": "online",
            "database": "healthy",
            "qdrant": qdrant_status,
            "telegram": "not_configured",
            "security_tier": "guarded",
            "active_samurai": 0,
        },
    )


@router.get("/metrics", response_model=ApiResponse)
async def get_system_metrics():
    """Return real-time system metrics (CPU, memory, disk)."""
    import psutil

    cpu_percent = psutil.cpu_percent(interval=0.3)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return ApiResponse(
        success=True,
        data={
            "cpu_percent": round(cpu_percent, 1),
            "memory_percent": round(mem.percent, 1),
            "memory_used_gb": round(mem.used / (1024 ** 3), 1),
            "memory_total_gb": round(mem.total / (1024 ** 3), 1),
            "disk_percent": round(disk.percent, 1),
            "disk_used_gb": round(disk.used / (1024 ** 3), 1),
            "disk_total_gb": round(disk.total / (1024 ** 3), 1),
        },
    )


@router.get("/overview", response_model=ApiResponse)
async def get_overview(
    agent_svc: AgentService = Depends(get_agent_service),
    mission_svc: MissionService = Depends(get_mission_service),
    security_svc: SecurityService = Depends(get_security_service),
):
    """Return overview dashboard payload."""
    # 1. Fetch Shogun Profile
    shogun_filters = [Agent.agent_type == "shogun", Agent.is_primary == True, Agent.is_deleted == False]
    shogun_records, _ = await agent_svc.get_all(filters=shogun_filters)
    shogun_name = shogun_records[0].name if shogun_records else "Shogun Prime"

    # 2. Fetch Active Samurai
    samurai_filters = [Agent.agent_type == "samurai", Agent.is_deleted == False]
    samurai_records, _ = await agent_svc.get_all(filters=samurai_filters)
    
    active_samurai_list = []
    for s in samurai_records:
        # Get the most recent in_progress or pending mission for this agent
        mission_filters = [
            Mission.assigned_agent_id == s.id,
            Mission.status.in_(["in_progress", "pending", "queued"])
        ]
        # We'll use a manual query here since BaseService doesn't support easy 'order_by' yet
        from sqlalchemy import desc
        stmt = select(Mission).where(*mission_filters).order_by(desc(Mission.created_at)).limit(1)
        res = await mission_svc.session.execute(stmt)
        curr_mission = res.scalars().first()
        
        active_samurai_list.append({
            "id": str(s.id),
            "name": s.name,
            "role": s.description or "Sub-agent",
            "status": s.status,
            "current_task": curr_mission.title if curr_mission else "Idle / No active task"
        })

    # 3. Fetch Security and Health Status
    qdrant_status = await _check_qdrant()
    # Read the actual persisted security posture
    from shogun.api.security import _get_agent_posture
    posture = await _get_agent_posture()
    security_tier = posture.get("active_tier", "tactical")

    return ApiResponse(
        success=True,
        data={
            "system_health": {
                "runtime": "online",
                "database": "healthy",
                "qdrant": qdrant_status,
                "telegram": "not_configured",
            },
            "shogun_profile": {
                "name": shogun_name,
                "status": "active"
            },
            "security_posture": {"tier": security_tier},
            "active_samurai": active_samurai_list,
            "recent_events": [
                {"type": "security", "message": "Unauthorized access attempt blocked", "timestamp": "2 mins ago"},
                {"type": "system", "message": "Database backup completed", "timestamp": "15 mins ago"},
                {"type": "agent", "message": "Neural lattice synchronized", "timestamp": "Recent"},
            ],
        },
    )


@router.get("/scan-local-models", response_model=ApiResponse)
async def scan_local_models(
    path: str = Query(..., description="Absolute path to the local model storage directory"),
):
    """Scan a local models directory and return discovered model names.

    Supports two layouts:
    - Ollama:    {path}/manifests/registry.ollama.ai/library/{model}/{tag}
    - LM Studio / generic: any *.gguf file found recursively under {path}
    """
    import os
    from pathlib import Path

    base = Path(path)
    if not base.exists():
        return ApiResponse(
            success=False,
            data=[],
            meta={"error": f"Path does not exist: {path}", "count": 0},
        )

    models: list[str] = []

    # ── Ollama manifest layout ──────────────────────────────────────
    # {path}/manifests/registry.ollama.ai/library/{model_name}/{tag}
    for registry_root in [
        base / "manifests" / "registry.ollama.ai" / "library",
        base / "manifests" / "registry.ollama.ai" / "models",
    ]:
        if registry_root.exists():
            for model_dir in sorted(registry_root.iterdir()):
                if model_dir.is_dir():
                    tags = sorted(t.name for t in model_dir.iterdir() if t.is_file())
                    for tag in tags:
                        entry = model_dir.name if tag == "latest" else f"{model_dir.name}:{tag}"
                        if entry not in models:
                            models.append(entry)

    # ── LM Studio / generic GGUF layout ────────────────────────────
    if not models:
        for root, _dirs, files in os.walk(base):
            for fname in sorted(files):
                if fname.lower().endswith(".gguf"):
                    name = fname[:-5]
                    if name not in models:
                        models.append(name)

    return ApiResponse(
        success=True,
        data=models,
        meta={"path": str(base), "count": len(models)},
    )


@router.get("/pull-model")
async def pull_model_stream(
    model: str = Query(..., description="Ollama model tag, e.g. llama3.2:3b"),
    base_url: str = Query("http://127.0.0.1:11434", description="Ollama base URL"),
):
    """Stream an Ollama model pull as Server-Sent Events.

    Each SSE event carries the raw JSON line from Ollama's /api/pull response:
    ``{"status": "pulling manifest"}``
    ``{"status": "pulling …", "completed": 131072, "total": 4661211296}``
    ``{"status": "success"}``

    After a successful pull, the model is auto-registered as an Ollama provider
    so it immediately appears in the Katana and Shogun model dropdowns.
    """
    import httpx
    from fastapi.responses import StreamingResponse

    async def event_stream():
        _pull_succeeded = False
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "POST",
                    f"{base_url}/api/pull",
                    json={"name": model, "stream": True},
                ) as resp:
                    async for line in resp.aiter_lines():
                        if line.strip():
                            yield f"data: {line}\n\n"
                            # Detect successful completion
                            try:
                                import json as _json
                                msg = _json.loads(line)
                                if msg.get("status") == "success":
                                    _pull_succeeded = True
                            except Exception:
                                pass
        except httpx.ConnectError:
            yield f'data: {{"status":"error","error":"Cannot connect to Ollama at {base_url}. Is it running?"}}\n\n'
        except Exception as exc:
            yield f'data: {{"status":"error","error":"{str(exc)}"}}\n\n'
        finally:
            # ── Auto-register as provider after successful pull ──
            if _pull_succeeded:
                try:
                    await _auto_register_ollama_provider(model, base_url)
                    yield f'data: {{"status":"registered","message":"Model \'{model}\' registered as provider"}}\n\n'
                except Exception as reg_exc:
                    import logging
                    logging.getLogger("shogun.system").warning(
                        "Auto-register failed for %s: %s", model, reg_exc
                    )
            yield 'data: {"status":"done"}\n\n'

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # disable nginx buffering if present
        },
    )


async def _auto_register_ollama_provider(model_name: str, base_url: str):
    """Register a pulled Ollama model as a provider if it doesn't already exist."""
    import json as _json
    from shogun.db.engine import async_session_factory
    from sqlalchemy import text

    async with async_session_factory() as session:
        # Check if already registered
        result = await session.execute(
            text("SELECT id FROM model_providers WHERE name = :name AND provider_type = 'ollama'"),
            {"name": model_name},
        )
        if result.scalar_one_or_none():
            return  # Already registered

        # Create new provider entry
        new_id = str(uuid.uuid4())
        slug = model_name.replace(":", "-").replace("/", "-").replace(".", "-")
        from datetime import datetime
        now = datetime.now().isoformat()

        await session.execute(
            text("""
                INSERT INTO model_providers (
                    id, provider_type, name, slug, base_url, auth_type, is_local,
                    status, health_status, config, created_at, updated_at, created_by, updated_by
                ) VALUES (
                    :id, 'ollama', :name, :slug, :base_url, 'none', 1,
                    'connected', 'healthy', :config, :now, :now, 'system', 'system'
                )
            """),
            {
                "id": new_id, "name": model_name, "slug": slug,
                "base_url": base_url, "config": _json.dumps({}), "now": now,
            },
        )
        await session.commit()

        import logging
        logging.getLogger("shogun.system").info(
            "Auto-registered Ollama model '%s' as provider (ID: %s)", model_name, new_id
        )


@router.get("/local-models", response_model=ApiResponse)
async def get_local_models(
    provider_type: str = Query(..., description="Provider type, e.g. 'ollama' or 'lmstudio'"),
    base_url: str = Query(..., description="Base URL of the provider"),
):
    """Proxy requests to local providers to retrieve currently loaded/downloaded models, avoiding CORS issues."""
    import httpx

    url = base_url.rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if provider_type == "ollama":
                resp = await client.get(f"{url}/api/tags")
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("name") or m.get("model") for m in data.get("models", [])]

                    # ── Auto-sync providers with Ollama ──
                    # Register new models, remove stale providers
                    try:
                        await _sync_ollama_providers(models, base_url)
                    except Exception:
                        pass  # Non-fatal

                    return ApiResponse(success=True, data=models)
                else:
                    return ApiResponse(
                        success=False,
                        data=[],
                        meta={"error": f"Ollama returned {resp.status_code}: {resp.text[:200]}"}
                    )
            else:
                # lmstudio or other OpenAI-compatible local provider
                resp = await client.get(f"{url}/models")
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("id") for m in data.get("data", [])]
                    return ApiResponse(success=True, data=models)
                else:
                    return ApiResponse(
                        success=False,
                        data=[],
                        meta={"error": f"Local provider returned {resp.status_code}: {resp.text[:200]}"}
                    )
    except httpx.ConnectError:
        return ApiResponse(
            success=False,
            data=[],
            meta={"error": f"Cannot connect to provider at {base_url}. Is it running?"}
        )
    except Exception as exc:
        return ApiResponse(
            success=False,
            data=[],
            meta={"error": str(exc)}
        )


async def _sync_ollama_providers(ollama_models: list[str], base_url: str):
    """Sync the model_providers table with Ollama's actual model list.

    - Registers any models present in Ollama but missing from providers.
    - Removes provider entries for models no longer in Ollama.
    """
    import json as _json
    import logging
    from shogun.db.engine import async_session_factory
    from sqlalchemy import text

    _log = logging.getLogger("shogun.system")

    async with async_session_factory() as session:
        # Get currently registered Ollama providers
        result = await session.execute(
            text("SELECT id, name FROM model_providers WHERE provider_type = 'ollama'")
        )
        registered = {row[1]: row[0] for row in result.fetchall()}

        ollama_set = set(ollama_models)
        registered_set = set(registered.keys())

        # Register new models
        new_models = ollama_set - registered_set
        for model_name in new_models:
            new_id = str(uuid.uuid4())
            slug = model_name.replace(":", "-").replace("/", "-").replace(".", "-")
            from datetime import datetime
            now = datetime.now().isoformat()
            await session.execute(
                text("""
                    INSERT INTO model_providers (
                        id, provider_type, name, slug, base_url, auth_type, is_local,
                        status, health_status, config, created_at, updated_at, created_by, updated_by
                    ) VALUES (
                        :id, 'ollama', :name, :slug, :base_url, 'none', 1,
                        'connected', 'healthy', :config, :now, :now, 'system', 'system'
                    )
                """),
                {"id": new_id, "name": model_name, "slug": slug,
                 "base_url": base_url, "config": _json.dumps({}), "now": now},
            )
            _log.info("Auto-registered Ollama model '%s' (synced from CLI)", model_name)

        # Remove stale providers (models no longer in Ollama)
        stale_models = registered_set - ollama_set
        for model_name in stale_models:
            await session.execute(
                text("DELETE FROM model_providers WHERE id = :id"),
                {"id": registered[model_name]},
            )
            _log.info("Removed stale Ollama provider '%s' (no longer installed)", model_name)

        if new_models or stale_models:
            await session.commit()


# ─────────────────────────────────────────────────────────────────────────────
# OLLAMA MODEL SEARCH (live from ollama.com)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/ollama-search", response_model=ApiResponse)
async def search_ollama_models(
    q: str = Query("", description="Search query"),
    p: int = Query(1, ge=1, description="Page number"),
    c: str = Query("", description="Capability filter (vision, tools, thinking, embedding, cloud)"),
):
    """Search the Ollama model registry at ollama.com/search.

    Returns parsed model data including name, description, sizes,
    capabilities, pull counts, and tags — proxied to avoid CORS.
    """
    import re
    import httpx
    import logging

    _log = logging.getLogger("shogun.system")

    params: dict[str, str] = {}
    if q.strip():
        params["q"] = q.strip()
    if p > 1:
        params["p"] = str(p)
    if c.strip():
        params["c"] = c.strip()

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                "https://ollama.com/search",
                params=params,
                headers={"User-Agent": "Shogun/1.0 (model-search)"},
            )
            if resp.status_code != 200:
                return ApiResponse(
                    success=False, data=[],
                    meta={"error": f"Ollama returned {resp.status_code}"}
                )
            html = resp.text
    except httpx.ConnectError:
        return ApiResponse(
            success=False, data=[],
            meta={"error": "Cannot connect to ollama.com. Check your internet."}
        )
    except Exception as exc:
        return ApiResponse(
            success=False, data=[],
            meta={"error": str(exc)[:300]}
        )

    # ── Parse model entries from HTML ──
    # Each model is in a <li x-test-model> block with an <a href="/library/{name}">
    models: list[dict] = []

    # Split by model list items
    model_blocks = re.split(r'<li\s+x-test-model', html)

    for block in model_blocks[1:]:  # skip the first chunk (before first model)
        model: dict = {}

        # Name: <span x-test-search-response-title>gemma4</span>
        name_match = re.search(r'x-test-search-response-title[^>]*>([^<]+)<', block)
        model["name"] = name_match.group(1).strip() if name_match else "unknown"

        # Description: <p class="...break-words...">description text</p>
        desc_match = re.search(r'break-words[^>]*>([^<]+)<', block)
        model["description"] = desc_match.group(1).strip() if desc_match else ""

        # Sizes: <span x-test-size ...>e4b</span>
        sizes = re.findall(r'x-test-size[^>]*>([^<]+)<', block)
        model["sizes"] = [s.strip() for s in sizes]

        # Capabilities: <span x-test-capability ...>vision</span>
        caps = re.findall(r'x-test-capability[^>]*>([^<]+)<', block)
        # Also check for cloud badge
        if 'cloud' in block.lower() and re.search(r'text-cyan-\d+[^>]*>cloud<', block):
            caps.append("cloud")
        model["capabilities"] = [c.strip() for c in caps]

        # Pulls: <span x-test-pull-count>11.3M</span>
        pulls_match = re.search(r'x-test-pull-count[^>]*>([^<]+)<', block)
        model["pulls"] = pulls_match.group(1).strip() if pulls_match else "0"

        # Tags count: <span x-test-tag-count>34</span>
        tags_match = re.search(r'x-test-tag-count[^>]*>([^<]+)<', block)
        model["tag_count"] = int(tags_match.group(1).strip()) if tags_match else 0

        # Updated: <span x-test-updated>1 week ago</span>
        updated_match = re.search(r'x-test-updated[^>]*>([^<]+)<', block)
        model["updated"] = updated_match.group(1).strip() if updated_match else ""

        # Default pull ID: use the model name (user can specify tags)
        model["id"] = model["name"]

        models.append(model)

    # Check for pagination: if there's a "Next" link or more pages
    has_more = bool(re.search(r'aria-label="Next Page"', html)) or bool(re.search(r'Next\s*</a>', html))
    # Alternative: check for page links beyond current
    if not has_more:
        has_more = bool(re.search(rf'[?&]p={p + 1}', html))

    _log.info("Ollama search q=%s p=%s: found %d models, has_more=%s", q, p, len(models), has_more)

    return ApiResponse(
        success=True,
        data={"models": models, "page": p, "has_more": has_more, "query": q},
    )

@router.delete("/delete-model")
async def delete_ollama_model(
    model: str = Query(..., description="Ollama model tag to delete, e.g. llama3.2:3b"),
    base_url: str = Query("http://127.0.0.1:11434", description="Ollama base URL"),
):
    """Delete a locally pulled Ollama model and remove its provider registration."""
    import httpx

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.request(
                "DELETE",
                f"{base_url}/api/delete",
                json={"name": model},
            )
            if resp.status_code == 200:
                # Auto-deregister the provider
                try:
                    from shogun.db.engine import async_session_factory
                    from sqlalchemy import text as _text
                    async with async_session_factory() as session:
                        await session.execute(
                            _text("DELETE FROM model_providers WHERE name = :name AND provider_type = 'ollama'"),
                            {"name": model},
                        )
                        await session.commit()
                except Exception:
                    pass  # Non-fatal — provider entry may not exist
                return {"success": True, "message": f"Model '{model}' deleted and deregistered."}
            else:
                err = resp.text[:300]
                return {"success": False, "message": f"Ollama returned {resp.status_code}: {err}"}
    except httpx.ConnectError:
        return {"success": False, "message": f"Cannot connect to Ollama at {base_url}. Is it running?"}
    except Exception as exc:
        return {"success": False, "message": str(exc)[:300]}


# ─────────────────────────────────────────────────────────────────────────────
# EXPORT / IMPORT BACKUP
# ─────────────────────────────────────────────────────────────────────────────

import io
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import File, Form, UploadFile
from fastapi.responses import Response, StreamingResponse as _StreamingResponse
from sqlalchemy import inspect, text
from shogun.db.engine import engine as _engine, async_session_factory


# Tables to include in the JSON export (all of them)
_EXPORT_TABLES: list[str] = [
    "agents", "personas", "samurai_profiles", "samurai_roles",
    "model_providers", "model_definitions", "model_routing_profiles",
    "tool_connectors", "secret_refs", "security_policies",
    "skill_sources", "skills", "skill_installations",
    "bushido_jobs", "bushido_recommendations", "bushido_schedules",
    "missions", "execution_events",
    "memory_records", "memory_provenance_links",
    "snapshots", "runtime_sessions",
    "operators", "kaizen_profiles", "kaizen_revisions",
    "workspaces", "workspace_peers", "workspace_messages",
    "alembic_version",
]

_SHOGUN_VERSION = "1.0.0"
_DB_PATH = PROJECT_ROOT / "data" / "shogun.db"


async def _dump_all_tables() -> dict[str, list[dict]]:
    """Return a {table_name: [row_dict, ...]} dump of every known table."""
    dump: dict[str, list[dict]] = {}
    async with async_session_factory() as session:
        for table in _EXPORT_TABLES:
            try:
                result = await session.execute(text(f"SELECT * FROM {table}"))
                rows = [dict(row._mapping) for row in result]
                # Coerce non-JSON-serialisable types to str
                clean = []
                for row in rows:
                    clean.append({
                        k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
                        for k, v in row.items()
                    })
                dump[table] = clean
            except Exception:
                dump[table] = []   # table may not exist yet
    return dump


def _build_zip(table_dump: dict, include_db: bool = True) -> bytes:
    """Bundle manifest + per-table JSON + optional raw .db into a ZIP in memory."""
    buf = io.BytesIO()
    now = datetime.now(timezone.utc)

    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Manifest
        manifest = {
            "shogun_version": _SHOGUN_VERSION,
            "backup_format": "1.0",
            "created_at": now.isoformat(),
            "tables": {t: len(rows) for t, rows in table_dump.items()},
            "total_rows": sum(len(r) for r in table_dump.values()),
            "includes_raw_db": include_db and _DB_PATH.exists(),
        }
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))

        # Per-table JSON files
        for table, rows in table_dump.items():
            zf.writestr(f"tables/{table}.json", json.dumps(rows, indent=2, default=str))

        # Raw SQLite file (most portable for a full restore)
        if include_db and _DB_PATH.exists():
            zf.write(_DB_PATH, "shogun.db")

    buf.seek(0)
    return buf.read()


@router.get("/backup/export")
async def export_backup(
    save_path: Optional[str] = None,
    include_db: bool = True,
):
    """Export a full Shogun backup as a ZIP file.

    - **Browser download** (default): returns the ZIP as an attachment.
    - **Server-side save**: pass `save_path` (absolute directory path) to write
      the file directly to that folder (e.g. ``C:/Users/you/Desktop``).

    The ZIP contains:
    - ``manifest.json`` — version, timestamp, row counts
    - ``tables/<name>.json`` — one JSON array per database table
    - ``shogun.db`` — raw SQLite file (when ``include_db=true``)
    """
    table_dump = await _dump_all_tables()
    zip_bytes = _build_zip(table_dump, include_db=include_db)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")
    filename = f"shogun_backup_{ts}.zip"

    if save_path:
        # ── Server-side save ──────────────────────────────────────────
        dest_dir = Path(save_path)
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_file = dest_dir / filename
            dest_file.write_bytes(zip_bytes)
        except Exception as exc:
            return ApiResponse(
                success=False,
                data={},
                meta={"error": f"Failed to write to path: {exc}"},
            )
        return ApiResponse(
            success=True,
            data={
                "saved_to": str(dest_file),
                "filename": filename,
                "size_bytes": len(zip_bytes),
                "tables": len(table_dump),
                "rows": sum(len(r) for r in table_dump.values()),
            },
        )

    # ── Browser download ──────────────────────────────────────────────
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(zip_bytes)),
        },
    )


@router.get("/backup/info")
async def backup_info():
    """Return a preview of what would be included in a backup (row counts per table)."""
    table_dump = await _dump_all_tables()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")
    return ApiResponse(
        success=True,
        data={
            "filename_preview": f"shogun_backup_{ts}.zip",
            "shogun_version": _SHOGUN_VERSION,
            "db_exists": _DB_PATH.exists(),
            "db_size_bytes": _DB_PATH.stat().st_size if _DB_PATH.exists() else 0,
            "tables": {t: len(rows) for t, rows in table_dump.items()},
            "total_rows": sum(len(r) for r in table_dump.values()),
        },
    )


@router.post("/backup/import")
async def import_backup(
    file: UploadFile = File(...),
    restore_mode: str = Form(default="json"),   # "json" | "db"
    wipe_first: bool = Form(default=True),
):
    """Restore a Shogun backup from an uploaded ZIP file.

    - **restore_mode=json** (recommended): reads each ``tables/<name>.json``
      file, truncates the table, and inserts all rows. Safe across schema versions.
    - **restore_mode=db**: replaces the raw ``shogun.db`` file directly
      (only works when the schema version matches exactly; requires restart).
    - **wipe_first**: when True, truncates each table before inserting (clean restore).
      Set to False for a merge/additive restore.
    """
    raw = await file.read()

    # Validate it's a valid zip
    try:
        zf = zipfile.ZipFile(io.BytesIO(raw))
    except zipfile.BadZipFile:
        return ApiResponse(success=False, data={}, meta={"error": "Invalid ZIP file"})

    names = zf.namelist()

    # Load and validate manifest
    if "manifest.json" not in names:
        return ApiResponse(success=False, data={}, meta={"error": "Missing manifest.json — not a valid Shogun backup"})

    manifest = json.loads(zf.read("manifest.json"))
    backup_version = manifest.get("backup_format", "unknown")

    if restore_mode == "db":
        # ── Raw DB restore ────────────────────────────────────────────
        if "shogun.db" not in names:
            return ApiResponse(success=False, data={}, meta={"error": "Backup does not include shogun.db (use restore_mode=json)"})

        db_bytes = zf.read("shogun.db")
        # Write to a temp file first, then atomically move
        tmp = _DB_PATH.with_suffix(".restore_tmp")
        tmp.write_bytes(db_bytes)
        # Keep the old DB as a safety backup
        bak = _DB_PATH.with_name(f"shogun.pre_restore.db")
        if _DB_PATH.exists():
            shutil.copy2(_DB_PATH, bak)
        shutil.move(str(tmp), str(_DB_PATH))

        return ApiResponse(
            success=True,
            data={
                "mode": "db",
                "restored_bytes": len(db_bytes),
                "previous_db_backed_up_to": str(bak),
                "message": "Raw database restored. Restart Shogun for changes to take effect.",
            },
        )

    # ── JSON table-by-table restore ───────────────────────────────────
    table_files = [n for n in names if n.startswith("tables/") and n.endswith(".json")]
    restored_tables: dict[str, int] = {}
    errors: list[str] = {}

    async with async_session_factory() as session:
        for tf in table_files:
            table_name = tf.removeprefix("tables/").removesuffix(".json")
            rows = json.loads(zf.read(tf))

            # Skip empty tables and the alembic_version table
            if not rows or table_name == "alembic_version":
                continue

            try:
                if wipe_first:
                    await session.execute(text(f"DELETE FROM {table_name}"))

                if rows:
                    # Build parameterised insert
                    cols = list(rows[0].keys())
                    placeholders = ", ".join(f":{c}" for c in cols)
                    col_list = ", ".join(cols)
                    stmt = text(f"INSERT OR IGNORE INTO {table_name} ({col_list}) VALUES ({placeholders})")
                    for row in rows:
                        await session.execute(stmt, row)

                restored_tables[table_name] = len(rows)
            except Exception as exc:
                errors[table_name] = str(exc)

        await session.commit()

    return ApiResponse(
        success=True,
        data={
            "mode": "json",
            "backup_format": backup_version,
            "backup_created_at": manifest.get("created_at"),
            "restored_tables": restored_tables,
            "total_rows_restored": sum(restored_tables.values()),
            "errors": errors,
        },
    )
