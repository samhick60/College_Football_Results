import dash
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

# Initialize Dash
app = Dash(__name__, external_stylesheets=["/assets/style.css"])
server = app.server  # for Flask integration later

# Placeholder data (replace with SQL query results)
df = pd.DataFrame({
    "category": ["A", "B", "C", "D"],
    "value": [10, 20, 15, 25]
})

# Layout
app.layout = html.Div(
    className="container",
    children=[
        html.H1("My Data Dashboard", className="title"),

        # Row 1
        html.Div(
            className="row",
            children=[
                dcc.Graph(id="graph-1"),
                dcc.Graph(id="graph-2")
            ]
        ),

        # Row 2
        html.Div(
            className="row",
            children=[
                dcc.Graph(id="graph-3"),
                dcc.Graph(id="graph-4")
            ]
        ),

        # Row 3
        html.Div(
            className="row",
            children=[
                dcc.Graph(id="graph-5"),
                dcc.Graph(id="graph-6")
            ]
        ),

        # Example filter
        html.Div(
            className="filter-section",
            children=[
                html.Label("Select Category:"),
                dcc.Dropdown(
                    id="category-filter",
                    options=[{"label": c, "value": c} for c in df["category"].unique()],
                    value="A",
                    clearable=False
                )
            ]
        )
    ]
)

# Callbacks
@app.callback(
    Output("graph-1", "figure"),
    Input("category-filter", "value")
)
def update_graph(selected_category):
    filtered = df[df["category"] == selected_category]
    fig = px.bar(filtered, x="category", y="value", title=f"Category {selected_category}")
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
