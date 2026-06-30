"""Office API Router — FastAPI endpoints for Katana Office App Mode.

All endpoints under /api/v1/office.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from shogun.schemas.common import ApiResponse
from shogun.schemas.office import (
    OfficeConfigResponse,
    OfficeConfigUpdate,
    OfficeStatusResponse,
    OfficeAppInfoResponse,
    PathValidationRequest,
    PathValidationResponse,
)

router = APIRouter(prefix="/office", tags=["Office"])
log = logging.getLogger("shogun.api.office")


# ── Status ───────────────────────────────────────────────────────────


@router.get("/status")
async def get_office_status():
    """Get Office App Mode status — detection results, config, process status."""
    try:
        from shogun.office.config import load_office_config
        from shogun.office.office_detector import detect_office_applications

        config = load_office_config()
        detection = detect_office_applications()

        # Get process manager status
        process_status = {}
        try:
            from shogun.office.process_manager import get_process_manager
            process_status = get_process_manager().get_status()
        except Exception:
            pass

        # Check if folders are configured
        folders_configured = bool(
            config.folders.input
            and config.folders.output
            and config.folders.templates
            and config.folders.temp
        )

        return ApiResponse(
            success=True,
            data=OfficeStatusResponse(
                enabled=config.enabled,
                platform_supported=detection.platform_supported,
                platform_name=detection.platform_name,
                minimum_posture=config.minimum_posture,
                message=detection.message,
                excel=OfficeAppInfoResponse(
                    name="Excel",
                    installed=detection.excel.installed,
                    version=detection.excel.version,
                    build=detection.excel.build,
                    path=detection.excel.path,
                    error=detection.excel.error,
                ),
                word=OfficeAppInfoResponse(
                    name="Word",
                    installed=detection.word.installed,
                    version=detection.word.version,
                    build=detection.word.build,
                    path=detection.word.path,
                    error=detection.word.error,
                ),
                powerpoint=OfficeAppInfoResponse(
                    name="PowerPoint",
                    installed=detection.powerpoint.installed,
                    version=detection.powerpoint.version,
                    build=detection.powerpoint.build,
                    path=detection.powerpoint.path,
                    error=detection.powerpoint.error,
                ),
                outlook=OfficeAppInfoResponse(
                    name="Outlook",
                    installed=detection.outlook.installed,
                    version=detection.outlook.version,
                    build=detection.outlook.build,
                    path=detection.outlook.path,
                    error=detection.outlook.error,
                ),
                folders_configured=folders_configured,
                process_status=process_status,
            ).model_dump(),
        )
    except Exception as exc:
        log.error("Failed to get Office status: %s", exc)
        return ApiResponse(
            success=False,
            error={"code": "office_status_error", "message": str(exc)},
        )


# ── Configuration ────────────────────────────────────────────────────


@router.get("/config")
async def get_office_config():
    """Get current Office App Mode configuration."""
    try:
        from shogun.office.config import load_office_config

        config = load_office_config()
        return ApiResponse(
            success=True,
            data=OfficeConfigResponse(**config.model_dump()).model_dump(),
        )
    except Exception as exc:
        log.error("Failed to load Office config: %s", exc)
        return ApiResponse(
            success=False,
            error={"code": "config_load_error", "message": str(exc)},
        )


@router.post("/config")
async def update_office_config(update: OfficeConfigUpdate):
    """Update Office App Mode configuration."""
    try:
        from shogun.office.config import load_office_config, save_office_config

        config = load_office_config()

        # Apply partial updates
        update_data = update.model_dump(exclude_none=True)
        for key, value in update_data.items():
            if isinstance(value, dict):
                # Merge nested objects
                current = getattr(config, key)
                if current is not None:
                    for k, v in value.items():
                        setattr(current, k, v)
            else:
                setattr(config, key, value)

        save_office_config(config)

        # Emit config change event
        try:
            from shogun.services.event_logger import EventLogger
            await EventLogger.emit_office_event(
                "office.config_changed",
                f"Office App Mode configuration updated",
                detail={"changes": update_data},
            )
        except Exception:
            pass

        return ApiResponse(
            success=True,
            data=OfficeConfigResponse(**config.model_dump()).model_dump(),
        )
    except Exception as exc:
        log.error("Failed to update Office config: %s", exc)
        return ApiResponse(
            success=False,
            error={"code": "config_save_error", "message": str(exc)},
        )


# ── Path Validation ──────────────────────────────────────────────────


@router.post("/validate-path")
async def validate_path(request: PathValidationRequest):
    """Validate a file path against Office folder boundaries."""
    try:
        from shogun.office.config import load_office_config
        from shogun.office.path_validator import FileBoundaryValidator, PathPurpose

        config = load_office_config()
        validator = FileBoundaryValidator(config)

        purpose = PathPurpose(request.purpose)
        result = validator.validate(request.file_path, purpose)

        return ApiResponse(
            success=True,
            data=PathValidationResponse(
                valid=result.is_valid,
                resolved_path=str(result.resolved_path),
                folder_type=result.folder_type.value,
                extension=result.extension,
            ).model_dump(),
        )
    except Exception as exc:
        # Path validation errors are expected — return them as data, not 500s
        error_message = str(exc)
        return ApiResponse(
            success=True,
            data=PathValidationResponse(
                valid=False,
                error=error_message,
            ).model_dump(),
        )


# ── Detection (on-demand re-scan) ────────────────────────────────────


@router.post("/detect")
async def detect_office():
    """Re-run Office application detection."""
    try:
        from shogun.office.office_detector import detect_office_applications

        detection = detect_office_applications()
        return ApiResponse(
            success=True,
            data=detection.to_dict(),
        )
    except Exception as exc:
        log.error("Office detection failed: %s", exc)
        return ApiResponse(
            success=False,
            error={"code": "detection_error", "message": str(exc)},
        )


# ── Cleanup ──────────────────────────────────────────────────────────


@router.post("/cleanup-temp")
async def cleanup_temp():
    """Clean up the Office temp folder."""
    try:
        from shogun.office.config import load_office_config
        from shogun.office.output_versioning import cleanup_temp_folder

        config = load_office_config()
        if not config.folders.temp:
            return ApiResponse(
                success=False,
                error={"code": "no_temp_folder", "message": "No temp folder configured."},
            )

        count = cleanup_temp_folder(config.folders.temp)
        return ApiResponse(
            success=True,
            data={"removed_count": count, "folder": config.folders.temp},
        )
    except Exception as exc:
        log.error("Temp cleanup failed: %s", exc)
        return ApiResponse(
            success=False,
            error={"code": "cleanup_error", "message": str(exc)},
        )


@router.post("/cleanup-outputs")
async def cleanup_outputs():
    """Clean up expired output files."""
    try:
        from shogun.office.config import load_office_config
        from shogun.office.output_versioning import cleanup_old_outputs

        config = load_office_config()
        if not config.folders.output:
            return ApiResponse(
                success=False,
                error={"code": "no_output_folder", "message": "No output folder configured."},
            )

        count = cleanup_old_outputs(
            config.folders.output,
            max_age_days=config.output_retention_days,
        )
        return ApiResponse(
            success=True,
            data={
                "removed_count": count,
                "folder": config.folders.output,
                "max_age_days": config.output_retention_days,
            },
        )
    except Exception as exc:
        log.error("Output cleanup failed: %s", exc)
        return ApiResponse(
            success=False,
            error={"code": "cleanup_error", "message": str(exc)},
        )
