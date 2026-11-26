"""
Pydantic schemas for conversations stored in public.conversations.
"""
from typing import Optional, Union
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ConversationBase(BaseModel):
    """Base fields for a conversation."""
    title: str = Field(..., min_length=1, max_length=255, description="Title of the conversation")


class ConversationCreate(ConversationBase):
    """Payload for creating a new conversation."""
    pass


class ConversationUpdate(BaseModel):
    """Payload for updating an existing conversation."""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="New title of the conversation")


class ConversationResponse(ConversationBase):
    """Representation of a conversation returned to the client."""
    id: str = Field(..., description="Unique conversation UUID")
    user_id: str = Field(..., description="UUID of the owning user (from auth.users)")
    created_at: Optional[Union[datetime, str]] = Field(None, description="Creation timestamp")
    updated_at: Optional[Union[datetime, str]] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)
