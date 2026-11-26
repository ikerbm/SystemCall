"""
Messages router: Manages public.messages respecting Supabase RLS.
Provides nested endpoints under conversations and direct message endpoints.
"""
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from supabase import Client
from postgrest.exceptions import APIError

from API.dependencies import get_authenticated_client, get_current_user
from API.schemas.message import MessageCreate, MessageResponse

# Router for nested messages under a specific conversation
conversation_messages_router = APIRouter(
    prefix="/conversations/{conversation_id}/messages",
    tags=["Messages"],
)

# Router for direct message actions by ID
messages_router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
)


@conversation_messages_router.get(
    "",
    response_model=List[MessageResponse],
    summary="List Messages in Conversation",
    description="Lists all messages for a given conversation in chronological order. RLS validates access.",
)
async def list_messages_for_conversation(
    conversation_id: str,
    limit: int = Query(100, ge=1, le=500, description="Max messages to retrieve"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    client: Client = Depends(get_authenticated_client),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[MessageResponse]:
    try:
        # First verify conversation exists / user has access to it
        conv_check = (
            client.table("conversations")
            .select("id")
            .eq("id", conversation_id)
            .execute()
        )
        if not conv_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation '{conversation_id}' not found or access denied.",
            )

        response = (
            client.table("messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            .order("created_at", desc=False)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return response.data or []
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
            detail=f"Unexpected error retrieving messages: {str(e)}",
        )


@conversation_messages_router.post(
    "",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Message to Conversation",
    description="Appends a new message (user, assistant, or system) into the conversation, respecting RLS.",
)
async def create_message_for_conversation(
    conversation_id: str,
    payload: MessageCreate,
    client: Client = Depends(get_authenticated_client),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> MessageResponse:
    try:
        # Verify conversation access under RLS
        conv_check = (
            client.table("conversations")
            .select("id")
            .eq("id", conversation_id)
            .execute()
        )
        if not conv_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation '{conversation_id}' not found or access denied.",
            )

        record = {
            "conversation_id": conversation_id,
            "role": payload.role,
            "content": payload.content,
            "tool_used": payload.tool_used,
        }
        response = client.table("messages").insert(record).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create message.",
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
            detail=f"Unexpected error creating message: {str(e)}",
        )


@messages_router.get(
    "/{message_id}",
    response_model=MessageResponse,
    summary="Get Message by ID",
    description="Retrieves a specific message. RLS restricts access to owner of parent conversation.",
)
async def get_message(
    message_id: str,
    client: Client = Depends(get_authenticated_client),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> MessageResponse:
    try:
        response = (
            client.table("messages")
            .select("*")
            .eq("id", message_id)
            .execute()
        )
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message '{message_id}' not found or access denied.",
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
            detail=f"Unexpected error retrieving message: {str(e)}",
        )


@messages_router.delete(
    "/{message_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Message by ID",
    description="Deletes a message if permitted by RLS policies.",
)
async def delete_message(
    message_id: str,
    client: Client = Depends(get_authenticated_client),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        response = (
            client.table("messages")
            .delete()
            .eq("id", message_id)
            .execute()
        )
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message '{message_id}' not found or deletion not permitted.",
            )
        return {
            "status": "success",
            "message": f"Message '{message_id}' successfully deleted.",
            "deleted_id": message_id,
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
            detail=f"Unexpected error deleting message: {str(e)}",
        )
