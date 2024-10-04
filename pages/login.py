import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, ctx, dash_table
from flask import Flask, session
from flask_session import Session
import pyodbc
import bcrypt
import pandas as pd
from sqlalchemy import create_engine

# Initialize the Flask server
server = Flask(__name__)
server.secret_key = 'supersecretkey'  # Replace with a strong secret key
server.config['SESSION_TYPE'] = 'filesystem'
Session(server)

# Initialize Dash app with suppress_callback_exceptions
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Database connection configuration
server_name = '3.143.112.247'
database_name = 'TNCOP'
username = 'iberissa'
password = 'IberisGlobal@123'

def get_db_connection():
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server_name};DATABASE={database_name};UID={username};PWD={password}"
    return pyodbc.connect(conn_str)

def get_db_engine():
    # SQL Server connection string format: 'mssql+pyodbc://<username>:<password>@<server>/<database>?driver=<driver>'
    conn_str = (
       "mssql+pyodbc://iberissa:IberisGlobal%40123@3.143.112.247/TNCOP"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    )
    return create_engine(conn_str)

def fetch_data_to_dataframe(query):
    engine = get_db_engine()
    try:
        # Execute the SQL query
        df = pd.read_sql_query(query, engine)
    except Exception as e:
        print(f"An error occurred: {e}")
        df = pd.DataFrame()  # Return an empty DataFrame in case of error
    
    return df

# Filter data based on a specific city
# city_filter = 'Chicago'
# filtered_df = df[df['City'] == city_filter]
# Example usage


# Define layout
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
], fluid=True)

dropdown_roles = pd.DataFrame({
    'District': ['Erode', 'Virudhunagar'],
    'Value': ['Erode', 'Virudhunagar']
})

# Protected page layout
def protected_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H2(f"Hello, {session.get('username')}!"))),
        dbc.Row(dbc.Col(html.H2(f"You're District is :, {session.get('district')}!"))),
        #dbc.Row(dbc.Col(html.Textarea(id='myh'))),
        #dbc.Row(dbc.Col(dbc.Button('Logout', id='logout-button', n_clicks=0))),
        dash_table.DataTable(id='filtered_df',page_size=10),
        dash_table.DataTable(id='filtered_df_sql',page_size=10)
    ], fluid=True)

@app.callback(
        Output('filtered_df_sql','data'),
        Output('filtered_df','data'),
        #Output('myh','value'),
        Input('url','pathname')
)
def update_content(pathname):
    # Default values for the outputs
    data_sql = []
    data = []
    text = ""

    query = "SELECT * FROM fact.Agewise_commodity"  # Replace with your SQL query
    dataframe_sql = fetch_data_to_dataframe(query)
    # Ensure we only handle the '/protected' page
    #if pathname == '/protected':
    # Load and filter data
    df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')
    district = session.get('district')
    
    # Filter DataFrame based on session data
    if district:
        df_filtered = df[df['continent'] == 'Asia']
        dataframe_sql1 =dataframe_sql[dataframe_sql['District']==district]
    else:
        df_filtered = df
        dataframe_sql1=dataframe_sql
    
    # Prepare data for DataTable
    data = df_filtered.to_dict('records')
    data_sql=dataframe_sql1.to_dict('records')
    # Prepare text for Textarea
    text = f"Filtered data for district: {district}" if district else "No district selected"
    
    return data_sql,data


# Registration page layout
def register_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H2("Register"))),
        dbc.Row([
            dbc.Col(dbc.Input(id='register-username', placeholder='Username', type='text')),
            dbc.Col(dbc.Input(id='register-password', placeholder='Password', type='password')),
            dbc.Col(dbc.Input(id='register-email', placeholder='Email', type='text')),
            html.Div(dcc.Dropdown(
                id='Role-dropdown',
                options=[{'label': District, 'value': District} for District in dropdown_roles['District']],
                value=dropdown_roles['District'][0]  # Default value             	
            ), style={'width': '200px'}),
            dbc.Col(dbc.Button('Register', id='register-button', n_clicks=0)),
        ]),
        dbc.Row(dbc.Col(html.Div(id='register-message'))),
        dbc.Row(dbc.Col(dbc.Button('Go to Login', href='/login'))),
    ], fluid=True)

# Login page layout
def login_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H2("Login"))),
        dbc.Row([
            dbc.Col(dbc.Input(id='login-username', placeholder='Username', type='text')),
            dbc.Col(dbc.Input(id='login-password', placeholder='Password', type='password')),
            dbc.Col(dbc.Button('Login', id='login-button', n_clicks=0)),
        ]),
        dbc.Row(dbc.Col(html.Div(id='login-message'))),
        dbc.Row(dbc.Col(dbc.Button('Go to Register', href='/register'))),
        
    ], fluid=True)


# 1. Display Page Content Based on URL Path                                          
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/register':
        return register_layout()
    elif pathname == '/login':
        return login_layout()
    elif pathname == '/protected':
        if 'username' in session:
            return protected_layout()
        else:
            return login_layout()  # Redirect to login if not authenticated
    else:
        return login_layout()  # Redirect to login if path not recognized

# 2. Handle Login Logic
@app.callback(
    Output('login-message', 'children'),
    Input('login-button', 'n_clicks'),
    State('login-username', 'value'),
    State('login-password', 'value')
)
def login(n_clicks, username, password):
    if n_clicks > 0:
        if username and password:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT password, email, district FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            conn.close()
            if user and bcrypt.checkpw(password.encode(), user.password.encode()):
                session['username'] = username
                session['email'] = user.email
                session['district'] = user.district
                return dcc.Location(pathname='/protected', id='redirect')
                #return dcc.Location(pathname='/page1', id='redirect')
            else:
                return "Invalid username or password."
        else:
            return "Please fill in both fields."
    return ""

# 3. Handle Registration Logic
@app.callback(
    Output('register-message', 'children'),
    Input('register-button', 'n_clicks'),
    State('register-username', 'value'),
    State('register-password', 'value'),
    State('register-email', 'value'),
    State('Role-dropdown', 'value')
)
def register(n_clicks, username, password, email, role):
    if n_clicks > 0:
        if username and password and email and role:
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password, email, district) VALUES (?, ?, ?, ?)",
                               (username, hashed_password.decode(), email, role))
                conn.commit()
                return dcc.Location(pathname='/login', id='redirect')
            except pyodbc.IntegrityError:
                return "Username already exists."
            finally:
                conn.close()
        else:
            return "Please fill in all fields."
    return ""

# Register the callbacks for login.py
def login_callbacks(app):
    @app.callback(
        Output('login-message', 'children'),
        Input('login-button', 'n_clicks'),
        State('login-username', 'value'),
        State('login-password', 'value')
    )
    def login(n_clicks, username, password):
        if n_clicks > 0:
            if username and password:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT password, email, district FROM users WHERE username = ?", (username,))
                user = cursor.fetchone()
                conn.close()
                if user and bcrypt.checkpw(password.encode(), user.password.encode()):
                    session['username'] = username
                    session['email'] = user.email
                    session['district'] = user.district
                    return dcc.Location(pathname='/page1', id='redirect')
                else:
                    return "Invalid username or password."
            else:
                return "Please fill in both fields."
        return ""

    @app.callback(
        Output('register-message', 'children'),
        Input('register-button', 'n_clicks'),
        State('register-username', 'value'),
        State('register-password', 'value'),
        State('register-email', 'value'),
        State('Role-dropdown', 'value')
    )
    def register(n_clicks, username, password, email, role):
        if n_clicks > 0:
            if username and password and email and role:
                hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                conn = get_db_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO users (username, password, email, district) VALUES (?, ?, ?, ?)",
                                   (username, hashed_password.decode(), email, role))
                    conn.commit()
                    return dcc.Location(pathname='/login', id='redirect')
                except pyodbc.IntegrityError:
                    return "Username already exists."
                finally:
                    conn.close()
            else:
                return "Please fill in all fields."
        return ""

    # @app.callback(
    #     Output('url', 'pathname'),
    #     Input('logout-button', 'n_clicks')
    # )
    # def logout(n_clicks):
    #     if n_clicks > 0:
    #         session.pop('username', None)
    #         session.pop('district', None)
    #         return '/login'
    #     return ctx.triggered_id  # Default return value in case of no clicks

# Run the server
if __name__ == '__main__':
    app.run_server(debug=True, port=50)

