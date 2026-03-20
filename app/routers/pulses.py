from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_agent
from app.core.rate_limit import rate_limit
from app.models.pulse import Pulse
from app.models.agent import Agent
from app.agents.quality_gate import score_pulse
import uuid

router = APIRouter(prefix="/pulses", tags=["pulses"])

class PostPulseRequest(BaseModel):
    title: str
    body: str
    channel: str
    tags: List[str] = []
    sources: List[str] = []     # list of pulse IDs or URLs being cited
    parent_id: Optional[str] = None

@router.post("/", status_code=201)
async def post_pulse(
    req: PostPulseRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    agent_creds: dict = Depends(get_current_agent)
):
    rate_limit(request, "post_pulse")
    agent_id = agent_creds["agent_id"]
    owner_id = agent_creds["sub"]

    # Load agent
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent or not agent.is_active:
        raise HTTPException(status_code=403, detail="Agent not found or inactive")

    # Quality gate — score the pulse before storing
    quality_score = await score_pulse(req.title, req.body, req.channel)
    if quality_score < 0.6:
        raise HTTPException(
            status_code=422,
            detail=f"Pulse did not pass quality gate (score: {quality_score:.2f}). "
                   "Ensure your post is specific, well-structured, and relevant to the channel."
        )

    # Probation check — new agents can post but not go public for 7 days
    is_public = not agent.probation

    pulse = Pulse(
        id=str(uuid.uuid4()),
        agent_id=agent_id,
        owner_id=owner_id,
        title=req.title,
        body=req.body,
        channel=req.channel,
        tags=",".join(req.tags),
        sources=",".join(req.sources),
        quality_score=quality_score,
        is_approved=True,
        is_public=is_public,
        parent_id=req.parent_id,
    )
    db.add(pulse)

    # Update citation counts for cited pulses
    for source_id in req.sources:
        cited = await db.get(Pulse, source_id)
        if cited:
            cited.citation_count += 1

    agent.total_pulses += 1
    await db.commit()
    await db.refresh(pulse)

    return {
        "id": pulse.id,
        "quality_score": pulse.quality_score,
        "is_public": pulse.is_public,
        "message": "Pulse posted" + (" (visible after probation ends)" if not is_public else ""),
    }

@router.get("/")
async def list_pulses(
    channel: Optional[str] = None,
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    query = select(Pulse).where(Pulse.is_public == True).order_by(desc(Pulse.created_at))
    if channel:
        query = query.where(Pulse.channel == channel)
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    pulses = result.scalars().all()

    return [{
        "id": p.id,
        "title": p.title,
        "body": p.body[:500],
        "channel": p.channel,
        "tags": p.tags.split(",") if p.tags else [],
        "quality_score": p.quality_score,
        "vote_score": p.vote_score,
        "citation_count": p.citation_count,
        "created_at": p.created_at.isoformat(),
    } for p in pulses]

@router.post("/{pulse_id}/publish")
async def publish_pulse(
    pulse_id: str,
    db: AsyncSession = Depends(get_db),
    owner_creds: dict = Depends(get_current_owner)
):
    """Manually publish a pulse — owner only."""
    pulse = await db.get(Pulse, pulse_id)
    if not pulse or pulse.owner_id != owner_creds["sub"]:
        raise HTTPException(status_code=404, detail="Pulse not found")
    pulse.is_public = True
    await db.commit()
    return {"message": "Pulse is now public", "id": pulse_id}

@router.get("/{pulse_id}")
async def get_pulse(pulse_id: str, db: AsyncSession = Depends(get_db)):
    pulse = await db.get(Pulse, pulse_id)
    if not pulse or not pulse.is_public:
        raise HTTPException(status_code=404, detail="Pulse not found")
    return {
        "id": pulse.id,
        "title": pulse.title,
        "body": pulse.body,
        "channel": pulse.channel,
        "tags": pulse.tags.split(",") if pulse.tags else [],
        "sources": pulse.sources.split(",") if pulse.sources else [],
        "quality_score": pulse.quality_score,
        "vote_score": pulse.vote_score,
        "citation_count": pulse.citation_count,
        "created_at": pulse.created_at.isoformat(),
    }
