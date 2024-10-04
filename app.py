              
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
from flask import Flask, session
from flask_session import Session
import pyodbc
from sqlalchemy import create_engine
from pages.page1 import create_page1, register_callbacks as page1_callbacks
from pages.page2 import create_page2_layout as create_page2, register_page2_callbacks as page2_callbacks
from pages.page3 import create_page3_layout as create_page3, register_page3_callbacks as page3_callbacks

from pages.login import login_layout, register_layout, login_callbacks
                                                                           
                                                                                                              
from components.navbar import Navbar

# Initialize the Flask server
server = Flask(__name__)
server.secret_key = 'supersecretkey'  # Replace with a strong secret key
server.config['SESSION_TYPE'] = 'filesystem'
Session(server)

# Initialize the Dash app with a Bootstrap theme
app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP, '/assets/styles.css'])

#******************************************************************************************************** 

# Database connection configuration
server_name = '3.143.112.247'
database_name = 'TNCOP'
username = 'iberissa'
password = 'IberisGlobal@123'

def get_db_connection():
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server_name};DATABASE={database_name};UID={username};PWD={password}"
    return pyodbc.connect(conn_str)

def get_db_engine():
    conn_str = (
        "mssql+pyodbc://iberissa:IberisGlobal%40123@3.143.112.247/TNCOP"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    )
    return create_engine(conn_str)

def fetch_data_to_dataframe(query):
    engine = get_db_engine()
    try:
        df = pd.read_sql_query(query, engine)
    except Exception as e:
        print(f"An error occurred: {e}")
        df = pd.DataFrame()  # Return an empty DataFrame in case of error
    
    return df

# SQL query to fetch data
query = """SELECT [S#No] AS Transactions, Month, Year, [Product Type] AS [Product Category],
                  [Product Name] AS [Product Item], Supplier, 
                  CASE 
                      WHEN ([Product Type] IN ('PDS Provisions', 'PDS Provisions - PC Card') AND District = 'Virudhunagar') THEN 'PDS'
                      WHEN ([Product Type] IN ('PDS', 'Police') AND District = 'Erode') THEN 'PDS'
                      ELSE 'Non PDS' 
                  END AS [PDS & Non PDS], 
                  is_jpc AS [JPC & Non JPC], 
                  District, 
                  COALESCE(Purchased, 0) AS Quantity, 
                  COALESCE([Cost Price], 0) AS [Cost Price], 
                  COALESCE([Cost Value], 0) AS [Cost Value],
                  COALESCE([Resale Price], 0) AS [Resale Price], 
                  COALESCE([Resale Value], 0) AS [Resale Value], 
                  (COALESCE([Resale Value], 0) - COALESCE([Cost Value], 0)) AS Resale_Cost,
                  ROUND(CASE WHEN COALESCE([Cost Value], 0) <> 0 THEN 
                              (COALESCE([Resale Value], 0) - COALESCE([Cost Value], 0)) / COALESCE([Cost Value], 0) 
                              ELSE 0 END, 2) AS Return_on_Invest,
                  FORMAT(DATEFROMPARTS(Year, 
                      CASE Month
                          WHEN 'January' THEN 1 
                          WHEN 'February' THEN 2 
                          WHEN 'March' THEN 3 
                          WHEN 'April' THEN 4 
                          WHEN 'May' THEN 5 
                          WHEN 'June' THEN 6 
                          WHEN 'July' THEN 7 
                          WHEN 'August' THEN 8 
                          WHEN 'September' THEN 9 
                          WHEN 'October' THEN 10 
                          WHEN 'November' THEN 11 
                          WHEN 'December' THEN 12 
                          ELSE NULL END, 1), 'dd-MM-yyyy') AS Month_Year 
          FROM fact.tnc_purchase"""

dataframe_sql1 = fetch_data_to_dataframe(query)
#df = pd.read_csv('data.csv')                   
        
#********************************************************************************************************
                                     
# Define the layout of the app
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='navbar-container'),
    html.Div(
                                  
        className='container-sidebar',
        children=[
            html.Div(
                id='sidebar',             
                className='side-bar',
                children=[
                    dbc.Nav(
                        [
                            dbc.NavLink('Purchase Summary', href='/page1', id='link-page1'),
                            html.Hr(),
                            dbc.NavLink('Profit Margin', href='/page2', id='link-page2'),
                            html.Hr(),
                            dbc.NavLink('Sales Analysis', href='/page3', id='link-page3')
                        ],
                        vertical=True,
                        pills=True
                    )
                ]
            ),
            html.Div(
                id='page-content',
                className='main-content'
            )
        ]
    ),
    html.Footer(
        className='app-footer',
        children=[
            html.P("© 2024 Your Company. All rights reserved.", style={'text-align': 'center', 'margin': '0'})
        ]
    ),
                                          
])

# Register callbacks from login.py
login_callbacks(app)

# Register callbacks for pages
page1_callbacks(app, dataframe_sql1)
page2_callbacks(app, dataframe_sql1)
page3_callbacks(app, dataframe_sql1)

                              
                                          

# Callback to update page content and navbar based on URL
@app.callback(
    [Output('page-content', 'children'),
     Output('navbar-container', 'children'),
     Output('sidebar', 'style'),                           
     Output('link-page1', 'className'),
     Output('link-page2', 'className'),
     Output('link-page3', 'className')],
    [Input('url', 'pathname')]
)
def display_page(pathname):
    try:
        # Default link classes
        active_link_page1 = ''
        active_link_page2 = ''
        active_link_page3 = ''
        sidebar_style = {'display': 'block'}
        # Check if the user is authenticated
        if 'username' not in session:
            if pathname not in ('/', '/register'):
                return login_layout(), Navbar('Login', '', ''), {'display': 'none'}, '', '',''
            if pathname == '/':
                return login_layout(), Navbar('Login', '', ''), {'display': 'none'}, '', '',''
            elif pathname == '/register':
                return register_layout(), Navbar('Register', '', ''), {'display': 'none'}, '', '',''
            return html.Div([html.H3('404: Not Found'), html.P('The page you are looking for does not exist.')]), Navbar('404: Not Found', '', ''), {'display': 'none'}, '', '',''

        # Determine the active page and return the corresponding layout
        # Get the district from the session
        district = session.get('district')

        # Filter DataFrame based on the session district
        filtered_dataframe = dataframe_sql1
        if district:
            filtered_dataframe = dataframe_sql1[dataframe_sql1['District'] == district]
                                   
        if pathname == '/page1':
            active_link_page1 = 'active'
            return create_page1(filtered_dataframe), Navbar('Purchase Summary', 'Mar-2023', 'Mar-2024'),sidebar_style, active_link_page1, '', ''
        elif pathname == '/page2':
            active_link_page2 = 'active'
            return create_page2(filtered_dataframe), Navbar('Profit Margin', '', ''), sidebar_style,'', active_link_page2, ''
        elif pathname == '/page3':
            active_link_page3 = 'active'
            return create_page3(filtered_dataframe), Navbar('Sales Analysis', '', ''), sidebar_style, '','', active_link_page3
        else:
            return html.Div([html.H3('404: Not Found'), html.P('The page you are looking for does not exist.')]), Navbar('404: Not Found', '', ''), '', '', '',''
    except Exception as e:
        print(f"Error in display_page callback: {e}")
        return html.Div([html.H3('500: Internal Server Error'), html.P('An error occurred while loading the page.')]), Navbar('Error', '', ''), '', '', ''

# Callback for logout
@app.callback(
    Output('url', 'pathname'),
    Input('logoutbutton', 'n_clicks'),
    prevent_initial_call=True
)
def logout(n_clicks):
    if n_clicks:
        session.pop('username', None)
        session.pop('district', None)
        return '/'
    return dash.no_update

if __name__ == '__main__':
    app.run_server(debug=True)
