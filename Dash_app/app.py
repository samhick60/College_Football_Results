import dash

from dash import Dash, html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import numpy as np
import plotly.express as px
from datetime import date, datetime
import pandas as pd
import os
from supabase import Client, create_client
from dotenv import load_dotenv


##Date Functions
def week_decider(date):
    week0_start = datetime(datetime.today().year, 8, 29)
    diff = (date-week0_start).days//7
    return  diff

current_year = datetime.today().year
current_week = week_decider(datetime.today())




load_dotenv()


#API url, key, and client set up
url = os.getenv("SUPABASE_URL", "https://mfgyhrqqlnojbgadscsf.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, SUPABASE_KEY)


#Data pulls
response_full = (
        supabase.table("curated_current_data_raw")
            .select("*")
        .execute()
         )
full_data = pd.DataFrame(response_full.data)

response_weekly_points = (
        supabase.table("weekly_points_raw")
            .select("*")
        .execute()
         )
weekly_points = pd.DataFrame(response_weekly_points.data)

response_team_weekly = (
        supabase.table("weekly_points_team_raw")
            .select("*")
        .execute()
         )
team_points = pd.DataFrame(response_team_weekly.data)



#Data Curation for Tables
#Table 1: Current Points


Table1 = (weekly_points[(weekly_points['season'] == current_year) & (weekly_points["player"] != "100 | Undrafted")])

undrafted_team_table = (team_points[(team_points['season'] == current_year) & (team_points["player"] == "100 | Undrafted")])





Table1 =  (Table1.groupby("player")[["points","games_completed" ,"games_left"]]
          .sum()
          .reset_index()
          .sort_values(by="points", ascending=False))


Table2 = (full_data[full_data['season'] == current_year]
          .filter(items=['startDate','homePart', 'homeTeam','homePoints','homegamepoints', 'awaygamepoints', 'awayPoints' ,'awayTeam' ,'AwayPart', 'week', 'spread'] ))


undrafted_team_table = (undrafted_team_table.filter(items=['team', 'points'])
                        .groupby("team")["points"]
                        .sum()
                        .reset_index()
                        .sort_values(by="points", ascending=False))

Table2['startDate'] = pd.to_datetime(Table2['startDate'], utc=True)
Table2["startDate"] = Table2["startDate"].dt.tz_convert("America/Los_Angeles")
Table2 = Table2.sort_values(by="startDate", ascending=True)
Table2['startDate'] = Table2['startDate'].dt.strftime('%m/%d/%Y %I:%M %p')



# Initialize Dash
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # for Flask integration later

#Table/Graph Functions

def bootstrap_table(df):
    return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, size="sm")


full_data["Snapshot_Date"] = pd.to_datetime(full_data["Snapshot_Date"], utc=True).dt.tz_convert("America/Los_Angeles")

# Layout
app.layout = html.Div(
    className="container",
    children=[
        html.H1("Hickman College Football Challenge", className="title"),
        html.H6("Last Refresh:" + str(full_data["Snapshot_Date"].dt.strftime('%m/%d/%Y %I:%M %p').max()), style={"text-align": "center"}),

        # Row 1
        html.Div(
            className="row",
            children=[
                html.H1("Total Points"),
                html.Div(id="table-container1", className="table-wrapper")
            ]
        ),

        html.Br(),

        # Row 3
        html.Div(
            className="row",
            children=[
                html.H1("Weekly Matchups"),
                dbc.Row([
                    dbc.Col([
                        html.H6("Pick the Week:"),
                        dcc.Dropdown(
                            id="week-filter",
                            options=[{"label": c, "value": c} for c in sorted(full_data["week"].unique())],
                            value=current_week,
                            clearable=True
                        )
                    ], width=6),
                    dbc.Col([
                        html.H6("Pick the Participant:"),
                        dcc.Dropdown(
                            id="player-filter",
                            options=[{"label": c, "value": c} for c in sorted(Table1["player"].unique())],
                            value="1 | Sam",
                            clearable=True
                        )
                    ], width=6)
                ]),
                html.H1(" "),
                html.Div(id="table-container2", className="table-wrapper")
            ]
        ),
        html.Div(
            className="row",
            children=[
                html.H1("Undrafted Teams"),

                html.H1(" "),
                html.Div(id="table-container3", className="table-wrapper")
            ]
        ),


    ]
)



# Callbacks
@app.callback(
    Output("table-container1", "children"),
    Output("table-container2", "children"),
    Output("table-container3", "children"),
    Input("week-filter", "value"),
    Input("player-filter", "value")
)
def update_tables(selected_week, selected_player):
    filtered1 = Table1
    filtered2 = Table2[(Table2["week"] == selected_week) & ((Table2["homePart"] == selected_player) | (Table2["AwayPart"] == selected_player))]
    filtered2 = filtered2.drop(columns='week')
    filtered3 = undrafted_team_table
    return bootstrap_table(filtered1),  bootstrap_table(filtered2), bootstrap_table(filtered3)



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)
