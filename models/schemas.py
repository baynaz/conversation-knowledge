from pydantic import BaseModel
from datetime import datetime


class TeamsMessage(BaseModel):
    thread_id: str
    parent_message_id: str | None = None
    author: str
    timestamp: datetime
    content: str
    channel: str | None = None