from datetime import date
from datetime import date, datetime
import pandas as pd
import requests
import os

from pandas import to_datetime
from supabase import Client, create_client
from dotenv import load_dotenv


#CollegeFootballData.com download information
load_dotenv()

CFD_API_KEY=os.getenv("CFD_API_KEY")
CFD_BASE_URL="https://api.collegefootballdata.com/games"
betting_url="https://api.collegefootballdata.com/lines"
ranking_url="https://api.collegefootballdata.com/rankings"

#SupaBase Connection
url = "https://mfgyhrqqlnojbgadscsf.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, SUPABASE_KEY)

today = datetime.today()

def year_decider(date):
    if date > datetime(today.year, 8, 29):
        return today.year
    else:
        return today.year - 1

current_season = year_decider(today)


def get_games(year, url):
    headers = {"Authorization": f"Bearer {CFD_API_KEY}"}
    params = {"year": year, "classification" : "fbs"}  # you can add week, team, etc.

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_lines(year, url, betProvider):
    headers = {"Authorization": f"Bearer {CFD_API_KEY}"}
    params = {"year": year, "classification" : "fbs", "provider" : betProvider}  # you can add week, team, etc.

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    res = response.json()
    df = pd.DataFrame(res)
    expanded = pd.json_normalize(df["lines"].explode())
    df = df.join(expanded)
    df = df.drop(columns=["lines"])
    df = df.fillna(0)
    dict = df.to_dict("records")
    return dict


def get_rankings(year, url):
    headers = {"Authorization": f"Bearer {CFD_API_KEY}"}
    params = {"year": year}  # you can add week, team, etc.

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    res = response.json()
    df = pd.DataFrame(res)
    expanded = pd.json_normalize(df["polls"].explode())
    df = df.join(expanded)
    expanded = pd.json_normalize(df["ranks"].explode())
    df = df.join(expanded)
    df = df.drop(columns=["ranks"])
    df = df.drop(columns=["polls"])
    df = df.fillna(0)
    dict = df.to_dict("records")
    return dict




def delete_and_upload(table_name,dict_data):

    supabase.table(f"{table_name}").delete().neq("id", 0).execute()

    supabase.table(f"{table_name}").insert(dict_data).execute()


#df.to_csv("C:/Users/samhi/OneDrive/Desktop/Hickman_Sports_Data/data2.csv")


if __name__ == '__main__':
    games = get_games(current_season, CFD_BASE_URL)
    bets = get_lines(current_season, betting_url, 'ESPN Bet')
    rankings = get_rankings(current_season, ranking_url)
    delete_and_upload('CollegeFootballData_raw', games)
    delete_and_upload('BettingData_current',bets)
    delete_and_upload('RankingData_current', rankings)