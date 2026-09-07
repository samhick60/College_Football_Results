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
week0_start = datetime(today.year, 8, 29)
week1_start = datetime(today.year, 9, 5)
D1_Conferences = ["ACC", "Big 12", "Big Ten", "Pac-12", "SEC", "FBS Independents", "Mountain West"]

def year_decider(date):
    if date > datetime(today.year, 8, 29):
        return today.year
    else:
        return today.year - 1

current_season = year_decider(today)


def week_decider(date):

    diff = (date-week0_start).days//7
    return  diff

def get_games(year, url):
    headers = {"Authorization": f"Bearer {CFD_API_KEY}"}
    params = {"year": year, "classification" : "fbs"}  # you can add week, team, etc.

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    res = response.json()
    df = pd.DataFrame(res)
    df['Snapshot_Date'] = today.isoformat()
    df = df.fillna(0)
    df['id'] = df['id'].astype(int)
    df['season'] = df['season'].astype(int)
    df['awayPoints'] = df['awayPoints'].astype(int)
    df['homePoints'] = df['homePoints'].astype(int)
    df['week'] = df['week'].astype(int)
    df['venueId'] = df['venueId'].astype(int)
    df['homeId'] = df['homeId'].astype(int)
    df['awayId'] = df['awayId'].astype(int)
    df = df.to_dict("records")

    return df

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
    df['Snapshot_Date'] = today.isoformat()
    df = df.fillna(0)
    df['id'] = df['id'].astype(int)
    df['season'] = df['season'].astype(int)
    df['week'] = df['week'].astype(int)
    df['homeTeamId'] = df['homeTeamId'].astype(int)
    df['homeScore'] = df['homeScore'].astype(int)
    df['awayTeamId'] = df['awayTeamId'].astype(int)
    df['awayScore'] = df['awayScore'].astype(int)
    df = df.to_dict("records")

    return df


def get_rankings(year, url):
    headers = {"Authorization": f"Bearer {CFD_API_KEY}"}
    params = {"year": year}  # you can add week, team, etc.

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    res = response.json()
    if not res:
        print("No rankings data returned.")
        return []

    all_rows = []

    # Iterate through each week object
    for week_obj in res:
        season = week_obj.get("season")
        week = week_obj.get("week")

        # Iterate through polls for that week
        for poll in week_obj.get("polls", []):
            poll_name = poll.get("poll")

            # Only keep AP Top 25
            if poll_name not in ["AP Top 25",	"Playoff Committee Rankings"]:
                continue

            # Flatten rankings for this poll
            for ranking in poll.get("ranks", []):
                row = {

                    "season": season,
                    "week": week,
                    "seasonType": week_obj.get("seasonType"),
                    "poll": poll_name,
                    "rank": ranking.get("rank"),
                    "school": ranking.get("school"),
                    "teamId": ranking.get("teamId"),
                    "conference": ranking.get("conference"),
                    "firstPlaceVotes": ranking.get("firstPlaceVotes"),
                    "points": ranking.get("points"),
                    "Snapshot_Date": today.isoformat()
                }
                all_rows.append(row)

    # Convert to DataFrame
    df = pd.DataFrame(all_rows)

    # Filter to D1 conferences if desired
    df = df[df["conference"].isin(D1_Conferences)]

    # Remove duplicates (same team/week/poll)
    df = df.drop_duplicates(subset=["poll", "season", "week", "school"])

    # Fill nulls
    df = df.fillna(0)

    # Convert to dict records for Supabase upload
    dictdf = df.to_dict("records")
    return dictdf




def delete_and_upload(table_name,dict_data):

    supabase.table(f"{table_name}").delete().neq("id", 0).execute()

    supabase.table(f"{table_name}").insert(dict_data).execute()


def update_week_team_ownership():
    response = (
        supabase.table("team_w_ownership")  # <-- your view name
        .select("*")
        .execute()
    )
    df = pd.DataFrame(response.data)
    df['Week'] = week_decider(today)
    dict_data = df.to_dict("records")
    supabase.table("team_w_ownership").insert(dict_data).execute()
    return

'''
df = get_lines(current_season, betting_url, 'DraftKings')
#df.to_csv("C:/Users/samhi/OneDrive/Desktop/Hickman_Sports_Data/data2.csv")
print(df.dtypes)
'''


if __name__ == '__main__':
    games = get_games(current_season, CFD_BASE_URL)
    bets = get_lines(current_season, betting_url, 'DraftKings')
    rankings = get_rankings(current_season, ranking_url)
    delete_and_upload('CollegeFootballData_current', games)
    delete_and_upload('BettingData_current',bets)
    delete_and_upload('RankingData_current', rankings)

