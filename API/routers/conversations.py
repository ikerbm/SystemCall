"""
Conversations router: Manages public.conversations respecting Supabase RLS.
"""
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from supabase import Client
from postgrest.exceptions import APIError

from API.dependencies import get_authenticated_client, get_current_user
from API.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
)

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.get(
    "",
    response_model=List[ConversationResponse],
    summary="List Conversations",
    description="Lists conversations belonging to the authenticated user. Row Level Security filters rows.",
)
async def list_conversations(
    limit: int = Query(50, ge=1, le=100, description="Max records to retrieve"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    client: Client = Depends(get_authenticated_client),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[ConversationResponse]:
    try:
        query = (
            client.table("conversations")
            .select("*")
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
        )
        response = query.execute()
        return response.data or []
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database query error: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error retrieving conversations: {str(e)}",
        )


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Conversation",
    description="Creates a new conversation record in public.conversations for the authenticated user.",
)
async def create_conversation(
    payload: ConversationCreate,
    client: Client = Depends(get_authenticated_client),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> ConversationResponse:
    try:
        record = {
            "title": payload.title,
            "user_id": current_user["id"],
        }
        response = client.table("conversations").insert(record).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create conversation.",
            )
        return response.data[0]
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database insert error: {e.message}",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error creating conversation: {str(e)}",
        )


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
    summary="Get Conversation by ID",
    description="Retrieves a specific conversation. Returns 404 if not found or unauthorized via RLS.",
)
async def get_conversation(
    conversation_id: str,
    client: Client = Depends(get_authenticated_client),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> ConversationResponse:
    try:
        response = (
            client.table("conversations")
            .select("*")
            .eq("id", conversation_id)
            .execute()
        )
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation '{conversation_id}' not found or access denied.",
            )
        return response.data[0]
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database query error: {e.message}",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error retrieving conversation: {str(e)}",
        )


@router.patch(
    "/{conversation_id}",
    response_model=ConversationResponse,
    summary="Update Conversation",
    description="Updates conversation attributes (e.g. title) for the authenticated user.",
)
async def update_conversation(
    conversation_id: str,
    payload: ConversationUpdate,
    client: Client = Depends(get_authenticated_client),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> ConversationResponse:
    update_data = {}
    if payload.title is not None:
        update_data["title"] = payload.title

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update.",
        )

    try:
        response = (
            client.table("conversations")
            .update(update_data)
            .eq("id", conversation_id)
            .execute()
        )
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation '{conversation_id}' not found or update not permitted.",
            )
        return response.data[0]
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database update error: {e.message}",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error updating conversation: {str(e)}",
        )


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Conversation",
    description="Deletes a conversation and cascaded records, respecting RLS.",
)
async def delete_conversation(
    conversation_id: str,
    client: Client = Depends(get_authenticated_client),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        response = (
            client.table("conversations")
            .delete()
            .eq("id", conversation_id)
            .execute()
        )
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation '{conversation_id}' not found or deletion not permitted.",
            )
        return {
            "status": "success",
            "message": f"Conversation '{conversation_id}' successfully deleted.",
            "deleted_id": conversation_id,
        }
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database deletion error: {e.message}",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error deleting conversation: {str(e)}",
        )
