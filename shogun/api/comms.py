"""Shared Comms/Telegram conversation API."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from shogun.api.deps import get_db
from shogun.db.models.chat_message import ChatMessage
from shogun.schemas.common import ApiResponse
from shogun.services.chat_sync_service import (
    append_chat_message,
    list_chat_messages,
    serialize_chat_message,
)

router = APIRouter(prefix="/comms", tags=["Comms"])


@router.get("/messages", response_model=ApiResponse)
async def get_messages(
    limit: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    messages = await list_chat_messages(db, limit=limit)
    return ApiResponse(data=[serialize_chat_message(message) for message in messages])


@router.post("/messages", response_model=ApiResponse, status_code=201)
async def create_message(
    body: dict,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    role = str(body.get("role", "")).strip().lower()
    content = str(body.get("content", "")).strip()
    if role not in {"user", "assistant", "shogun"}:
        raise HTTPException(400, "role must be user, assistant, or shogun")
    if not content:
        raise HTTPException(400, "content is required")

    client_message_id = body.get("client_message_id")
    existing = None
    if client_message_id:
        existing = await db.scalar(
            select(ChatMessage).where(ChatMessage.client_message_id == client_message_id)
        )
    message = await append_chat_message(
        db,
        channel="comms",
        role="assistant" if role == "shogun" else role,
        content=content,
        client_message_id=client_message_id,
        message_data=body.get("message_data") if isinstance(body.get("message_data"), dict) else {},
    )

    if existing is None and body.get("mirror_to_telegram", True):
        from shogun.services.notification_service import send_channel_message

        speaker = "You" if role == "user" else "Shogun"
        background_tasks.add_task(
            send_channel_message,
            f"{speaker} (Comms):\n{content}",
            channel="telegram",
            event_type="comms.chat.message",
        )

    return ApiResponse(data=serialize_chat_message(message))


@router.delete("/messages", response_model=ApiResponse)
async def clear_messages(db: AsyncSession = Depends(get_db)):
    result = await db.execute(delete(ChatMessage))
    return ApiResponse(data={"deleted": result.rowcount or 0})
