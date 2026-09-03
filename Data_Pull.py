from datetime import date, datetime
import pandas as pd
import requests
import os
from supabase import Client, create_client
from dotenv import load_dotenv

load_dotenv()

#API url, key, and client set up
url = "https://mfgyhrqqlnojbgadscsf.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, SUPABASE_KEY)

response = (
    supabase.table("curated_current_data")   # <-- your view name
            .select("*")
            .execute()
)
df = pd.DataFrame(response.data)

print(df)