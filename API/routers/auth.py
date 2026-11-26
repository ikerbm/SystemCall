"""
Authentication router: Provides endpoints for user login, signup, session refresh, logout,
and protected token verification with Supabase Auth.
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from supabase_auth.errors import AuthApiError, AuthError

from API.database import get_supabase_client
from API.dependencies import get_current_user, get_token
from API.schemas.auth import (
    AuthSessionResponse,
    AuthVerifyResponse,
    LoginRequest,
    RefreshTokenRequest,
    SignUpRequest,
    SignUpResponse,
    UserResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=AuthSessionResponse,
    summary="User Login",
    description="Authenticates a user with email and password using Supabase Auth, returning access and refresh tokens.",
)
async def login(payload: LoginRequest) -> AuthSessionResponse:
    """
    Log in using email and password.
    Returns: Access token (JWT), refresh token, and user details.
    """
    client = get_supabase_client()
    try:
        auth_response = client.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password,
        })
        
        session = auth_response.session
        user = auth_response.user
        
        if not session or not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login failed: Invalid credentials or inactive session.",
            )

        user_data = UserResponse(
            id=str(user.id),
            email=user.email,
            role=user.role,
            user_metadata=user.user_metadata or {},
            app_metadata=user.app_metadata or {},
            created_at=str(user.created_at) if user.created_at else None,
        )

        return AuthSessionResponse(
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            token_type=session.token_type or "bearer",
            expires_in=session.expires_in,
            user=user_data,
        )

    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {e.message}",
        )
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Supabase Auth error: {str(e)}",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected login error: {str(e)}",
        )


@router.post(
    "/signup",
    response_model=SignUpResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Registers a new user in Supabase Auth with email and password.",
)
async def sign_up(payload: SignUpRequest) -> SignUpResponse:
    """
    Register a new user account.
    """
    client = get_supabase_client()
    try:
        credentials = {
            "email": payload.email,
            "password": payload.password,
        }
        if payload.user_metadata:
            credentials["options"] = {"data": payload.user_metadata}

        auth_response = client.auth.sign_up(credentials)
        user = auth_response.user
        session = auth_response.session

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signup failed: User was not created.",
            )

        user_data = UserResponse(
            id=str(user.id),
            email=user.email,
            role=user.role,
            user_metadata=user.user_metadata or {},
            app_metadata=user.app_metadata or {},
            created_at=str(user.created_at) if user.created_at else None,
        )

        session_data = None
        if session:
            session_data = AuthSessionResponse(
                access_token=session.access_token,
                refresh_token=session.refresh_token,
                token_type=session.token_type or "bearer",
                expires_in=session.expires_in,
                user=user_data,
            )

        message = (
            "Registration successful. Please check your email to confirm your account."
            if not session
            else "Registration successful."
        )

        return SignUpResponse(
            message=message,
            user=user_data,
            session=session_data,
        )

    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {e.message}",
        )
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Supabase Auth error: {str(e)}",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected signup error: {str(e)}",
        )


@router.post(
    "/refresh",
    response_model=AuthSessionResponse,
    summary="Refresh Session Token",
    description="Renews an expired access token using a valid Supabase refresh token.",
)
async def refresh_token(payload: RefreshTokenRequest) -> AuthSessionResponse:
    """
    Exchange a refresh token for a fresh access token and refresh token.
    """
    client = get_supabase_client()
    try:
        auth_response = client.auth.refresh_session(payload.refresh_token)
        session = auth_response.session
        user = auth_response.user

        if not session or not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to refresh session. Invalid or expired refresh token.",
            )

        user_data = UserResponse(
            id=str(user.id),
            email=user.email,
            role=user.role,
            user_metadata=user.user_metadata or {},
            app_metadata=user.app_metadata or {},
            created_at=str(user.created_at) if user.created_at else None,
        )

        return AuthSessionResponse(
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            token_type=session.token_type or "bearer",
            expires_in=session.expires_in,
            user=user_data,
        )

    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Session refresh failed: {e.message}",
        )
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Supabase Auth error: {str(e)}",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error refreshing session: {str(e)}",
        )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User Logout",
    description="Logs out the user and revokes the active session.",
)
async def logout(
    token: str = Depends(get_token),
) -> Dict[str, str]:
    """
    Terminates the active user session.
    """
    client = get_supabase_client(token=token)
    try:
        client.auth.sign_out()
        return {"message": "Logged out successfully."}
    except Exception as e:
        # Even if logout fails remotely, return successful logout acknowledgement
        return {"message": "Session terminated locally."}


@router.get(
    "/verify",
    response_model=AuthVerifyResponse,
    summary="Verify JWT Authentication",
    description="Validates the caller's Supabase JWT Bearer token and returns user status and metadata.",
)
async def verify_auth(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> AuthVerifyResponse:
    """
    Protected endpoint to test and verify authentication.
    Requires header: `Authorization: Bearer <access_token>`.
    """
    user_model = UserResponse(**current_user)
    return AuthVerifyResponse(
        status="authenticated",
        message="Authentication token is valid and active in Supabase Auth.",
        user=user_model,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User Profile",
    description="Retrieves the profile and metadata of the currently authenticated Supabase user.",
)
async def get_me(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> UserResponse:
    """
    Returns authenticated user information.
    """
    return UserResponse(**current_user)
