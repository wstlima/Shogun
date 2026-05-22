"""Tests for the system heartbeat scheduling and rescheduling functionality."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone
import uuid

from shogun.scheduler import (
    get_scheduler,
    register_heartbeat_job,
    reschedule_heartbeat,
    _run_heartbeat,
)
from shogun.db.models.agent import Agent


@pytest.fixture(autouse=True)
def clean_scheduler():
    """Ensure the scheduler is clean and not running tasks between tests."""
    sched = get_scheduler()
    for job in list(sched.get_jobs()):
        sched.remove_job(job.id)
    yield
    for job in list(sched.get_jobs()):
        sched.remove_job(job.id)


@pytest.mark.asyncio
async def test_reschedule_heartbeat():
    """Test that rescheduling successfully adds or updates the heartbeat job."""
    sched = get_scheduler()
    assert sched.get_job("system_heartbeat") is None

    # Reschedule to 10 minutes
    await reschedule_heartbeat(10)
    job = sched.get_job("system_heartbeat")
    assert job is not None
    # APScheduler interval trigger stores target in minutes or interval
    assert job.trigger.interval.total_seconds() == 600

    # Reschedule to 25 minutes
    await reschedule_heartbeat(25)
    job = sched.get_job("system_heartbeat")
    assert job is not None
    assert job.trigger.interval.total_seconds() == 1500


@pytest.mark.asyncio
async def test_register_heartbeat_job_default():
    """Test registering heartbeat job falls back to 15 mins if primary agent not found."""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = None
    mock_session.execute.return_value = mock_result

    sched = get_scheduler()
    assert sched.get_job("system_heartbeat") is None

    await register_heartbeat_job(mock_session)

    job = sched.get_job("system_heartbeat")
    assert job is not None
    assert job.trigger.interval.total_seconds() == 900  # 15 minutes


@pytest.mark.asyncio
async def test_register_heartbeat_job_custom_agent_setting():
    """Test registering heartbeat job reads frequency from primary agent settings."""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    
    # Create a fake primary shogun agent
    agent = Agent(
        id=uuid.uuid4(),
        name="Test Shogun",
        agent_type="shogun",
        is_primary=True,
        is_deleted=False,
        bushido_settings={"heartbeat_frequency": 42}
    )
    
    mock_result.scalars().first.return_value = agent
    mock_session.execute.return_value = mock_result

    sched = get_scheduler()
    await register_heartbeat_job(mock_session)

    job = sched.get_job("system_heartbeat")
    assert job is not None
    assert job.trigger.interval.total_seconds() == 42 * 60  # 42 minutes


@pytest.mark.asyncio
@patch("shogun.db.engine.async_session_factory")
@patch("shogun.services.email_service.EmailService")
@patch("shogun.services.event_logger.EventLogger.emit_system_event")
async def test_run_heartbeat_execution(mock_emit, mock_email_svc_class, mock_session_factory):
    """Test the _run_heartbeat background job execution logic."""
    mock_session = AsyncMock()
    mock_session_factory.return_value.__aenter__.return_value = mock_session
    
    # Setup mock agent
    agent = Agent(
        id=uuid.uuid4(),
        name="Test Shogun",
        agent_type="shogun",
        is_primary=True,
        is_deleted=False,
        status="active"
    )
    
    mock_agent_result = MagicMock()
    mock_agent_result.scalars().all.return_value = [agent]
    
    # Setup mock session execute to return the active agent
    mock_session.execute.return_value = mock_agent_result

    # Mock email service behavior
    mock_email_svc = AsyncMock()
    mock_email_svc_class.return_value = mock_email_svc
    mock_email_acc = MagicMock()
    mock_email_acc.is_active = True
    mock_email_acc.perm_read_mail = True
    mock_email_acc.email_address = "test@example.com"
    mock_email_svc.get_account.return_value = mock_email_acc

    # Run heartbeat
    await _run_heartbeat()

    # Assertions
    assert agent.last_heartbeat_at is not None
    mock_email_svc.fetch_folders.assert_called_once()
    assert mock_email_acc.last_sync_at is not None
    mock_session.commit.assert_called_once()
    mock_emit.assert_called_once_with(
        event_type="system.heartbeat",
        action="System heartbeat processed. Active agents: 1. Email synced: True",
        detail={"agent_count": 1, "email_sync_success": True}
    )
