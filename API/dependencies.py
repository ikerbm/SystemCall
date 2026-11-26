"""
FastAPI dependencies for authentication, token extraction, and Supabase client injection.
Enforces JWT validation with Supabase Auth and injects user-scoped Supabase clients for RLS.
"""
from typing import Any, Dict, Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client
from supabase_auth.errors import AuthApiError, AuthError

from API.config import settings
from API.database import get_supabase_client

# Bearer token extractor
security = HTTPBearer(auto_error=False)


def get_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    Extracts the JWT Bearer token from the Authorization header.
    Raises 401 Unauthorized if the header is missing or not a Bearer token.
    """
    if not credentials or credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Bearer authorization token in request headers.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


async def get_current_user(
    token: str = Depends(get_token)
) -> Dict[str, Any]:
    """
    Validates the JWT token against Supabase Auth.
    
    1. First attempts validation via Supabase Auth API (`client.auth.get_user(token)`).
    2. If offline/network issues occur and SUPABASE_JWT_SECRET is configured,
       falls back to local cryptographic decoding with PyJWT.
    3. Returns normalized user profile dictionary with 'id', 'email', 'role', and metadata.
    """
    client = get_supabase_client()

    try:
        # Primary validation: Supabase Auth server validation
        user_response = client.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = user_response.user
        return {
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
            "user_metadata": user.user_metadata or {},
            "app_metadata": user.app_metadata or {},
            "created_at": str(user.created_at) if user.created_at else None,
        }

    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {e.message}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Supabase auth error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
        # Fallback to local JWT verification if SUPABASE_JWT_SECRET is set
        if settings.SUPABASE_JWT_SECRET:
            try:
                payload = jwt.decode(
                    token,
                    settings.SUPABASE_JWT_SECRET,
                    algorithms=["HS256"],
                    options={"verify_aud": False}
                )
                user_id = payload.get("sub")
                if not user_id:
                    raise ValueError("Token missing 'sub' claim")
                return {
                    "id": str(user_id),
                    "email": payload.get("email"),
                    "role": payload.get("role", "authenticated"),
                    "user_metadata": payload.get("user_metadata", {}),
                    "app_metadata": payload.get("app_metadata", {}),
                    "created_at": None,
                }
            except Exception as jwt_err:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Token validation failed: {str(jwt_err)}",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication validation failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_authenticated_client(
    token: str = Depends(get_token)
) -> Client:
    """
    Returns a Supabase Client configured with the caller's JWT token.
    All PostgREST queries through this client forward the user's Bearer token,
    ensuring that Postgres Row Level Security (RLS) is strictly enforced.
    """
    return get_supabase_client(token=token)
