import dash

from dash import Dash, html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
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




load_dotenv()

#API url, key, and client set up
url = "https://mfgyhrqqlnojbgadscsf.supabase.co"
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



#Data Curation for Tables
#Table 1: Current Points
Table1 = (weekly_points[(weekly_points['season'] == current_year) & (weekly_points["player"] != "100 | Undrafted")]
          .copy()
          .groupby("player")["points"]
          .sum()
          .reset_index()
          .sort_values(by="points", ascending=False)
          )

Table2 = (full_data[full_data['season'] == current_year]
          .filter(items=['homePart', 'homeTeam','homePoints','homegamepoints', 'awaygamepoints', 'awayPoints' ,'awayTeam' ,'AwayPart', 'week'] ))

# Initialize Dash
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP,"/assets/style.css"])
server = app.server  # for Flask integration later

#Table/Graph Functions

def bootstrap_table(df):
    return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, size="sm")


current_week = week_decider(datetime.today())

# Layout
app.layout = html.Div(
    className="container",
    children=[
        html.H1("Hickman College Football Challenge", className="title"),
        html.H6("Last Refresh:" + str(full_data["Snapshot_Date"].max()), style={"text-align": "center"}),

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
                html.H6("Pick the Week:"),
                dcc.Dropdown(
                    id="week-filter",
                    options=[{"label": c, "value": c} for c in sorted(full_data["week"].unique())],
                    value=current_week,
                    clearable=True
                ),
                html.H6("Pick the Participant:"),
                dcc.Dropdown(
                    id="player-filter",
                    options=[{"label": c, "value": c} for c in sorted(Table1["player"].unique())],
                    value="1 | Sam",
                    clearable=True
                ),
                html.H1(" "),
                html.Div(id="table-container2", className="table-wrapper")
            ]
        ),

        # Example filter
    ]
)



# Callbacks
@app.callback(
    Output("table-container1", "children"),
    Output("table-container2", "children"),
    Input("week-filter", "value"),
    Input("player-filter", "value")
)
def update_tables(selected_week, selected_player):
    filtered1 = Table1
    filtered2 = Table2[(Table2["week"] == selected_week) & ((Table2["homePart"] == selected_player) | (Table2["AwayPart"] == selected_player))]

    return bootstrap_table(filtered1),  bootstrap_table(filtered2)


if __name__ == "__main__":
    app.run(debug=True)
