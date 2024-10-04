import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

# Sample data and plot for Home Page
df = pd.DataFrame({
    "x": [1, 2, 3, 4, 5],
    "y": [5, 10, 15, 20, 25]
})
fig = px.line(df, x="x", y="y", title="Welcome to the Dashboard")

layout = html.Div([
    dcc.Graph(figure=fig),
    html.H3('Welcome to the Dashboard'),
    html.P('This is the home page of the dashboard.')
])
