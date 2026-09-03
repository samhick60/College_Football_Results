import math

import requests
import os
from datetime import date, datetime
import pandas as pd
import games_data_upload
from pandas import to_datetime
from supabase import Client, create_client
from dotenv import load_dotenv
today = datetime.today()
today = datetime(today.year, 9, 19)

#CollegeFootballData.com download information
load_dotenv()


#SupaBase Connection
url = "https://mfgyhrqqlnojbgadscsf.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, SUPABASE_KEY)

today = datetime.today()
D1_Conferences = ["ACC", "Big 12", "Big Ten", "Pac-12", "SEC", "FBS Independents", "Mountain West"]

def clean_value(value):

    if pd.isna(value):
        return None

    if isinstance(value, float) and not math.isfinite(value):
        return None

    return value


def clean_dataframe_for_json(df):
    return df.map(clean_value)



def year_decider(date):
    if date > datetime(today.year, 8, 29):
        return today.year
    else:
        return today.year - 1

current_season = year_decider(today)


df = pd.read_csv("C:/Users/samhi/Downloads/CurrentTeamsWOwnership_rows.csv")

df = clean_dataframe_for_json(df)

table_name = "currentteamswownership"

dict_data = df.to_dict("records")


supabase.table(f"{table_name}").insert(dict_data).execute()

week = games_data_upload.week_decider(today)
print(week)