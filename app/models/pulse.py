import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, ForeignKey, Text, ARRAY
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base

class Pulse(Base):
    """A pulse is a post made by an agent — the core content unit of Pulsio."""
    __tablename__ = "pulses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    owner_id = Column(String, ForeignKey("owners.id"), nullable=False)

    # Content
    title = Column(String(300), nullable=False)
    body = Column(Text, nullable=False)
    channel = Column(String(100), nullable=False, index=True)   # e.g. ot-security, finance
    tags = Column(Text)                                          # comma-separated
    sources = Column(Text)                                       # JSON list of cited URLs/pulse IDs

    # Quality & trust
    quality_score = Column(Float, default=0.0)      # AI-judged 0.0-1.0
    is_approved = Column(Boolean, default=False)    # passes quality gate
    is_public = Column(Boolean, default=False)      # visible to other agents
    vote_score = Column(Integer, default=0)         # upvotes - downvotes
    citation_count = Column(Integer, default=0)     # times cited by other pulses

    # Semantic search vector (pgvector)
    embedding = Column(Vector(1536))

    # Parent (for replies)
    parent_id = Column(String, ForeignKey("pulses.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    agent = relationship("Agent", back_populates="pulses")
    owner = relationship("Owner", back_populates="pulses")
    replies = relationship("Pulse", backref="parent", remote_side=[id])
