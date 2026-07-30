import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Deleting all fake leads...")
res1 = supabase.table('leads').delete().in_('status', ['NEW', 'GOOD', 'NOT_INTERESTED', 'RETRY']).execute()
print(f"Deleted leads.")

print("Resetting scrape jobs...")
res2 = supabase.table('scrape_jobs').delete().in_('status', ['PENDING', 'PROCESSING', 'COMPLETED', 'FAILED']).execute()
print("Deleted scrape jobs.")

print("Database is clean and ready for real data!")
