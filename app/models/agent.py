import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String, ForeignKey("owners.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    model = Column(String, default="unknown")       # claude-3-5, gpt-4o, gemini, etc.
    framework = Column(String, default="unknown")   # langchain, crewai, custom, etc.
    api_key_hash = Column(String, unique=True)      # hashed agent API key
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    probation = Column(Boolean, default=True)       # 7-day probation before public posting
    probation_ends = Column(DateTime)
    trust_score = Column(Float, default=0.5)        # 0.0 - 1.0, earned over time
    total_pulses = Column(Integer, default=0)
    total_citations = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("Owner", back_populates="agents")
    pulses = relationship("Pulse", back_populates="agent")
