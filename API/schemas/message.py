"""
Pydantic schemas for messages stored in public.messages.
"""
from typing import Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class MessageBase(BaseModel):
    """Base fields for a message."""
    role: str = Field(..., min_length=1, max_length=50, description="Author role (user, assistant, system, etc.)")
    content: str = Field(..., min_length=1, description="Textual or serialized content of the message")
    tool_used: Optional[Any] = Field(None, description="Information or metadata about the tool used, if any")


class MessageCreate(MessageBase):
    """Payload for appending a message to a conversation."""
    pass


class MessageResponse(MessageBase):
    """Representation of a message returned to the client."""
    id: Union[str, int] = Field(..., description="Unique message ID")
    conversation_id: str = Field(..., description="UUID of the parent conversation")
    created_at: Optional[Union[datetime, str]] = Field(None, description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True)
