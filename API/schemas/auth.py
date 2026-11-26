"""
Pydantic schemas for authentication and user verification.
"""
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class UserResponse(BaseModel):
    """Represents a validated Supabase user."""
    id: str = Field(..., description="Unique user identifier from auth.users (UUID)")
    email: Optional[str] = Field(None, description="User email address")
    role: Optional[str] = Field(None, description="User role, e.g. 'authenticated'")
    user_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom user metadata")
    app_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Application metadata")
    created_at: Optional[str] = Field(None, description="Account creation timestamp")

    model_config = ConfigDict(from_attributes=True)


class AuthVerifyResponse(BaseModel):
    """Response returned by the protected authentication verification endpoint."""
    status: str = Field(default="authenticated", description="Authentication state")
    message: str = Field(default="Authentication token is valid.", description="Status message")
    user: UserResponse = Field(..., description="Validated user details")


class LoginRequest(BaseModel):
    """Payload for user login."""
    email: str = Field(..., min_length=3, description="User email address")
    password: str = Field(..., min_length=6, description="User password")


class SignUpRequest(BaseModel):
    """Payload for user registration."""
    email: str = Field(..., min_length=3, description="User email address")
    password: str = Field(..., min_length=6, description="User password")
    user_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional custom user metadata")


class RefreshTokenRequest(BaseModel):
    """Payload for refreshing an expired access token."""
    refresh_token: str = Field(..., min_length=1, description="Supabase refresh token")


class AuthSessionResponse(BaseModel):
    """Response containing JWT tokens and user session data."""
    access_token: str = Field(..., description="JWT Bearer access token")
    refresh_token: Optional[str] = Field(None, description="Refresh token for renewing sessions")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: Optional[int] = Field(None, description="Seconds until expiration")
    user: UserResponse = Field(..., description="User profile details")


class SignUpResponse(BaseModel):
    """Response returned on user signup."""
    message: str = Field(..., description="Status message")
    user: Optional[UserResponse] = Field(None, description="User profile details")
    session: Optional[AuthSessionResponse] = Field(None, description="Session with tokens if auto-confirmed")
