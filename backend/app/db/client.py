from supabase import create_client, Client
from app.config import settings
_supabase_client = None
def get_supabase():
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
    return _supabase_client
class _LazySupabase:
    def __getattr__(self, name):
        return getattr(get_supabase(), name)
supabase = _LazySupabase()
