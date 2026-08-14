from supabase import Client, create_client
import pandas as pd


response = supabase.table("Participants").select("*").execute()

df = pd.DataFrame(response.data)

print(df)