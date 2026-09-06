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


def pull_full_date():
    response = (
        supabase.table("curated_current_data_raw")
            .select("*")
            .eq("season", 2026)
            .eq("week", 1)
        # Keep rows where either HomePart or AwayPart is NOT undrafted or NULL
            .or_("homePart.not.in.(NULL,100 | Undrafted),AwayPart.not.in.(NULL,100 | Undrafted)")

        .execute()
         )
    df = pd.DataFrame(response.data)
    return df


def pull_weekly_scores():
    response = (
        supabase.table("weekly_points_raw")
        .select("*")
        .eq("season", 2026)
        .eq("week", 1)
        # Keep rows where either HomePart or AwayPart is NOT undrafted or NULL

        .execute()
    )
    df = pd.DataFrame(response.data)
    return df


full = pull_full_date()
weekly = pull_weekly_scores()

full.to_csv("C:/Users/samhi/OneDrive/Desktop/Hickman_Sports_Data/data3.csv")
weekly.to_csv("C:/Users/samhi/OneDrive/Desktop/Hickman_Sports_Data/data2.csv")
