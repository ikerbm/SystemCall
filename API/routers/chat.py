"""
Chat router for querying Rafael AI.
Restricted exclusively to authenticated users with valid Supabase Auth JWTs.
Enforces Supabase Row Level Security (RLS) and automatically registers conversations and messages.
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from postgrest.exceptions import APIError

from API.dependencies import get_authenticated_client, get_current_user
from API.rafael_service import get_rafael
from API.schemas.chat import AskRequest, AskResponse, ChatRequest

router = APIRouter(
    tags=["Rafael AI Chat"],
)


@router.post(
    "/conversations/{conversation_id}/ask",
    response_model=AskResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask Rafael (Existing Conversation)",
    description="Sends a question to Rafael within an existing conversation. Only accessible by logged-in users. Stores both the user prompt and Rafael's response in Supabase.",
)
async def ask_rafael_in_conversation(
    conversation_id: str,
    payload: AskRequest,
    client: Client = Depends(get_authenticated_client),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> AskResponse:
    """
    1. Validates that the conversation belongs to the authenticated user via RLS.
    2. Saves the user's message in Supabase.
    3. Executes Rafael AI (`ask_rafael`) with conversation context.
    4. Saves Rafael's response in Supabase.
    5. Returns the complete exchange.
    """
    try:
        # Check conversation existence and ownership under RLS
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

        # 1. Insert user message in Supabase
        user_msg_res = (
            client.table("messages")
            .insert({
                "conversation_id": conversation_id,
                "role": "user",
                "content": payload.message,
                "tool_used": None,
            })
            .execute()
        )
        if not user_msg_res.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to record user message in database.",
            )
        user_message_data = user_msg_res.data[0]

        # 2. Query Rafael AI
        rafael = get_rafael()
        try:
            ai_reply = rafael.ask_rafael(payload.message, session_id=conversation_id)
        except Exception as ai_err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Rafael AI failed to generate response: {str(ai_err)}",
            )

        # 3. Insert assistant response in Supabase
        assistant_msg_res = (
            client.table("messages")
            .insert({
                "conversation_id": conversation_id,
                "role": "assistant",
                "content": ai_reply,
                "tool_used": None,
            })
            .execute()
        )
        if not assistant_msg_res.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record Rafael response in database.",
            )
        assistant_message_data = assistant_msg_res.data[0]

        return AskResponse(
            conversation_id=conversation_id,
            response=ai_reply,
            user_message=user_message_data,
            assistant_message=assistant_message_data,
        )

    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error: {e.message}",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error processing request: {str(e)}",
        )


@router.post(
    "/chat",
    response_model=AskResponse,
    status_code=status.HTTP_200_OK,
    summary="Direct Chat with Rafael",
    description="Convenience chat endpoint for logged-in users. Automatically creates a conversation in Supabase if no conversation_id is supplied, queries Rafael AI, and returns the response.",
)
async def chat_with_rafael(
    payload: ChatRequest,
    client: Client = Depends(get_authenticated_client),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> AskResponse:
    """
    Chat endpoint for logged-in users.
    - If conversation_id is provided, appends to it.
    - If conversation_id is omitted, creates a new conversation first.
    """
    conversation_id = payload.conversation_id

    try:
        if not conversation_id:
            # Generate automated conversation title
            title = payload.title or (
                payload.message[:35] + ("..." if len(payload.message) > 35 else "")
            )
            conv_res = (
                client.table("conversations")
                .insert({
                    "title": title,
                    "user_id": current_user["id"],
                })
                .execute()
            )
            if not conv_res.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to initialize new conversation in Supabase.",
                )
            conversation_id = conv_res.data[0]["id"]
        else:
            # Verify conversation under RLS
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

        # 1. Insert user message in Supabase
        user_msg_res = (
            client.table("messages")
            .insert({
                "conversation_id": conversation_id,
                "role": "user",
                "content": payload.message,
                "tool_used": None,
            })
            .execute()
        )
        if not user_msg_res.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to record user message in database.",
            )
        user_message_data = user_msg_res.data[0]

        # 2. Query Rafael AI
        rafael = get_rafael()
        try:
            ai_reply = rafael.ask_rafael(payload.message, session_id=conversation_id)
        except Exception as ai_err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Rafael AI failed to generate response: {str(ai_err)}",
            )

        # 3. Insert assistant response in Supabase
        assistant_msg_res = (
            client.table("messages")
            .insert({
                "conversation_id": conversation_id,
                "role": "assistant",
                "content": ai_reply,
                "tool_used": None,
            })
            .execute()
        )
        if not assistant_msg_res.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record Rafael response in database.",
            )
        assistant_message_data = assistant_msg_res.data[0]

        return AskResponse(
            conversation_id=conversation_id,
            response=ai_reply,
            user_message=user_message_data,
            assistant_message=assistant_message_data,
        )

    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error: {e.message}",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error processing chat request: {str(e)}",
        )
