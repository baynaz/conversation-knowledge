from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TeamsMessage(BaseModel):
    """A single raw message coming from Teams (or the simulator)."""
    id: str
    thread_id: str
    parent_message_id: Optional[str] = None
    author: str
    content: str
    channel: Optional[str] = None
    timestamp: datetime


class KnowledgeObject(BaseModel):
    """Structured knowledge extracted from a resolved thread."""
    thread_id: str
    problem: Optional[str] = None
    context: Optional[str] = None
    symptoms: list[str] = []
    solutions_tried: list[str] = []
    confirmed_solution: Optional[str] = None
    technology: Optional[str] = None