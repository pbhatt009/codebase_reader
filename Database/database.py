import os
from supabase import create_client, Client
def connect_db():
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    print(supabase)
    
    return supabase
    
