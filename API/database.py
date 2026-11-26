"""
Database connection management for Supabase.
Provides client factory functions to generate standard or user-scoped (RLS-compliant) clients.
"""
from typing import Optional
from supabase import create_client, Client, ClientOptions
#from supabase.lib.client_options import ClientOptions
from API.config import settings


def get_supabase_client(token: Optional[str] = None) -> Client:
    """
    Creates and returns a Supabase client.
    
    CRITICAL FOR ROW-LEVEL SECURITY (RLS):
    When `token` (the user's JWT from Supabase Auth) is provided,
    it is passed in the Authorization header to PostgREST.
    This causes Postgres to evaluate `auth.uid()` and enforce RLS policies
    specifically for that user.
    """
    url = settings.get_supabase_url()
    key = settings.get_supabase_key()

    if token:
        options = ClientOptions(headers={"Authorization": f"Bearer {token}"})
        return create_client(url, key, options=options)
    
    return create_client(url, key)


def get_supabase_admin_client() -> Client:
    """
    Creates and returns a Supabase client using the service role key (if configured).
    CAUTION: Service role key bypasses Row Level Security. Use only for administrative tasks.
    Falls back to standard client if service role key is not configured.
    """
    url = settings.get_supabase_url()
    service_key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.get_supabase_key()
    return create_client(url, service_key)
