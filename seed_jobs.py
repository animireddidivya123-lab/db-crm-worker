import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

categories = ["Kirana/Grocery Store", "Boutique/Designer Studio", "Restaurant/Cafe"]
states = ["Andhra Pradesh", "Telangana", "Karnataka"]

jobs = []
for state in states:
    for cat in categories:
        jobs.append({
            "state": state,
            "main_category": cat,
            "sub_category": cat,
            "target_count": 300,
            "status": "PENDING"
        })

res = supabase.table('scrape_jobs').insert(jobs).execute()
print(f"Successfully inserted {len(res.data)} scrape jobs for 300 leads each!")
