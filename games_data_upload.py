import requests
import os
from supabase import Client, create_client
from dotenv import load_dotenv

#CollegeFootballData.com download information
load_dotenv()

CFD_API_KEY=os.getenv("CFD_API_KEY")
CFD_BASE_URL=os.getenv("CFD_BASE_URL")

#SupaBase Connection
url = "https://mfgyhrqqlnojbgadscsf.supabase.co"
key = "sb_secret_OlPGe7osOdprcMz6s8405g_QsL8o-vf"

supabase: Client = create_client(url, key)




def get_games(year):
    headers = {"Authorization": f"Bearer {CFD_API_KEY}"}
    params = {"year": year, "classification" : "fbs"}  # you can add week, team, etc.

    response = requests.get(CFD_BASE_URL, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def delete_and_upload(table_name,dict_data):

    supabase.table(f"{table_name}").delete().neq("id", 0).execute()

    supabase.table(f"{table_name}").insert(dict_data).execute()



#df.to_csv("C:/Users/samhi/OneDrive/Desktop/Hickman_Sports_Data/data2.csv")


if __name__ == '__main__':
    games = get_games(2025)
    delete_and_upload('CollegeFootballData_raw',games)


