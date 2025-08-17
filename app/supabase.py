from supabase import create_client, Client
import os


def supabase_client() -> Client:
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SECRET_KEY')
    return create_client(url, key)
