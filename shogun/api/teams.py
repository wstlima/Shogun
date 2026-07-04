"""Katana Microsoft Teams adapter management and internal bridge API."""

from __future__ import annotations

import io
import json
import os
import uuid
import zipfile
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from shogun.api.deps import get_db
from shogun.config import settings
from shogun.db.models.teams import TeamsUserMap
from shogun.schemas.common import ApiResponse
from shogun.schemas.teams import CommandEnvelope, TeamsConfigUpdate, TeamsRoleUpdate
from shogun.services.teams_service import TeamsService

router = APIRouter(prefix="/katana/teams", tags=["Katana · Microsoft Teams"])
command_router = APIRouter(prefix="/katana/command", tags=["Katana · Command Channels"])


def get_teams_service(db: AsyncSession = Depends(get_db)) -> TeamsService:
    return TeamsService(db)


@router.get("/config", response_model=ApiResponse)
async def get_config(service: TeamsService = Depends(get_teams_service)):
    return ApiResponse(data=await service.get_config())


@router.put("/config", response_model=ApiResponse)
async def put_config(body: TeamsConfigUpdate, service: TeamsService = Depends(get_teams_service)):
    return ApiResponse(data=await service.update_config(body))


@router.post("/enable", response_model=ApiResponse)
async def enable(service: TeamsService = Depends(get_teams_service)):
    config = await service.get_config_model()
    config.enabled = True
    await service.db.flush()
    return ApiResponse(data=await service.get_config())


@router.post("/disable", response_model=ApiResponse)
async def disable(service: TeamsService = Depends(get_teams_service)):
    config = await service.get_config_model()
    config.enabled = False
    await service.db.flush()
    return ApiResponse(data=await service.get_config())


@router.get("/health", response_model=ApiResponse)
async def health(service: TeamsService = Depends(get_teams_service)):
    return ApiResponse(data=await service.health())


@router.post("/test/backend", response_model=ApiResponse)
async def test_backend(service: TeamsService = Depends(get_teams_service)):
    return ApiResponse(data={"ok": True, "component": "shogun_backend", "health": await service.health()})


@router.post("/test/graph", response_model=ApiResponse)
async def test_graph(service: TeamsService = Depends(get_teams_service)):
    config = await service.get_config_model()
    if not config.graph_enabled:
        return ApiResponse(data={"ok": False, "error": "Microsoft Graph is disabled"})
    return ApiResponse(
        data={
            "ok": False,
            "error": "Graph credential validation is performed by the customer-hosted Teams Bridge.",
        }
    )


@router.post("/test/proactive-message", response_model=ApiResponse)
async def test_proactive(service: TeamsService = Depends(get_teams_service)):
    config = await service.get_config_model()
    return ApiResponse(
        data={
            "ok": False,
            "error": "Proactive messaging is disabled"
            if not config.proactive_enabled
            else "No target conversation was supplied to the external Teams Bridge",
        }
    )


@router.get("/commands", response_model=ApiResponse)
async def commands(limit: int = 100, service: TeamsService = Depends(get_teams_service)):
    return ApiResponse(data=await service.list_commands(limit))


@router.get("/users", response_model=ApiResponse)
async def users(service: TeamsService = Depends(get_teams_service)):
    return ApiResponse(data=await service.list_users())


@router.put("/users/{user_id}/role", response_model=ApiResponse)
async def update_role(
    user_id: uuid.UUID,
    body: TeamsRoleUpdate,
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(TeamsUserMap, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Teams user mapping not found")
    user.shogun_role = body.shogun_role
    user.allowed_command_groups = body.allowed_command_groups
    await db.flush()
    return ApiResponse(data={"id": str(user.id), "shogun_role": user.shogun_role})


@router.post("/manifest/generate")
@router.get("/manifest/download")
async def manifest(service: TeamsService = Depends(get_teams_service)):
    try:
        package = await service.generate_manifest_package()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return StreamingResponse(
        io.BytesIO(package),
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="shogun-teams-app.zip"'},
    )


@router.post("/manifest/validate", response_model=ApiResponse)
async def validate_manifest(service: TeamsService = Depends(get_teams_service)):
    try:
        package = await service.generate_manifest_package()
        with zipfile.ZipFile(io.BytesIO(package)) as archive:
            names = set(archive.namelist())
            manifest_data = json.loads(archive.read("manifest.json"))
        required = {"manifest.json", "color.png", "outline.png"}
        issues = [] if required.issubset(names) else [f"Missing files: {sorted(required - names)}"]
        if not manifest_data.get("bots"):
            issues.append("Manifest has no bot capability")
        return ApiResponse(
            data={"valid": not issues, "issues": issues, "manifest_version": manifest_data.get("manifestVersion")}
        )
    except ValueError as exc:
        return ApiResponse(data={"valid": False, "issues": [str(exc)]})


@router.post("/diagnostics/export")
async def diagnostics(service: TeamsService = Depends(get_teams_service)):
    config = await service.get_config()
    # Secret references and user message contents are deliberately excluded.
    config.pop("client_secret_ref", None)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "health": await service.health(),
        "config": config,
        "recent_commands": [
            {k: v for k, v in row.items() if k not in {"normalized_text", "user_id"}}
            for row in await service.list_commands(50)
        ],
    }
    return StreamingResponse(
        io.BytesIO(json.dumps(payload, default=str, indent=2).encode()),
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="shogun-teams-diagnostics.json"'},
    )


@command_router.post("/dispatch", response_model=ApiResponse)
async def dispatch(
    envelope: CommandEnvelope,
    authorization: str | None = Header(default=None),
    service: TeamsService = Depends(get_teams_service),
):
    expected_key = os.environ.get("SHOGUN_INTERNAL_API_KEY")
    if expected_key:
        if authorization != f"Bearer {expected_key}":
            raise HTTPException(status_code=401, detail="Invalid bridge credential")
    elif settings.is_production:
        raise HTTPException(status_code=503, detail="Bridge authentication is not configured")
    if envelope.source != "microsoft_teams":
        raise HTTPException(status_code=400, detail="This adapter currently accepts Microsoft Teams envelopes")
    response = await service.dispatch(envelope)
    return ApiResponse(data={"response_envelope": response.model_dump(mode="json")})
