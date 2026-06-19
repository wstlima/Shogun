"""Nexus gateway authentication handler module."""

from __future__ import annotations

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from shogun.api.deps import get_db
from shogun.db.models.nexus import ExternalAgentModel
from shogun.nexus.core.agent_registry import AgentRegistry

# Define standard HTTP Bearer authentication dependency
security = HTTPBearer(auto_error=False)


async def get_authenticated_agent(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
    db: AsyncSession = Depends(get_db)
) -> ExternalAgentModel:
    """Authenticates the incoming request via standard Bearer token.
    
    Raises 401 Unauthorized if token is missing, invalid, or belongs to an inactive agent.
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication token is missing. Please provide 'Authorization: Bearer <your_token>'."
        )

    token = credentials.credentials
    registry = AgentRegistry(db)
    agent = await registry.get_agent_by_token(token)
    
    if not agent:
        raise HTTPException(
            status_code=401,
            detail="Invalid or unrecognized Nexus authentication token."
        )
        
    if not agent.is_active:
        raise HTTPException(
            status_code=403,
            detail=f"The external agent account '{agent.name}' is registered but has been marked inactive."
        )

    return agent
