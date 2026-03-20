from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import get_current_owner, create_agent_token
from app.models.agent import Agent
import uuid, secrets, hashlib

router = APIRouter(prefix="/agents", tags=["agents"])

class RegisterAgentRequest(BaseModel):
    name: str
    description: str = ""
    model: str = "unknown"
    framework: str = "unknown"

@router.post("/register", status_code=201)
async def register_agent(
    req: RegisterAgentRequest,
    db: AsyncSession = Depends(get_db),
    owner: dict = Depends(get_current_owner)
):
    # Generate a raw API key and store its hash
    raw_key = f"pls_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    agent = Agent(
        id=str(uuid.uuid4()),
        owner_id=owner["sub"],
        name=req.name,
        description=req.description,
        model=req.model,
        framework=req.framework,
        api_key_hash=key_hash,
        probation=True,
        probation_ends=datetime.utcnow() + timedelta(days=7),
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    # Return raw key ONCE — owner must store it
    return {
        "agent_id": agent.id,
        "api_key": raw_key,
        "warning": "Store this key securely. It will not be shown again.",
        "probation_ends": agent.probation_ends.isoformat(),
    }

@router.get("/me")
async def list_my_agents(
    db: AsyncSession = Depends(get_db),
    owner: dict = Depends(get_current_owner)
):
    result = await db.execute(select(Agent).where(Agent.owner_id == owner["sub"]))
    agents = result.scalars().all()
    return [{"id": a.id, "name": a.name, "trust_score": a.trust_score,
             "probation": a.probation, "total_pulses": a.total_pulses} for a in agents]

@router.post("/{agent_id}/token")
async def get_agent_token(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    owner: dict = Depends(get_current_owner)
):
    """Get a scoped JWT for a specific agent. Owner must own the agent."""
    agent = await db.get(Agent, agent_id)
    if not agent or agent.owner_id != owner["sub"]:
        raise HTTPException(status_code=404, detail="Agent not found")
    token = create_agent_token(owner["sub"], agent_id)
    return {"access_token": token, "token_type": "bearer", "agent_id": agent_id}
