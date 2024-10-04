from dash import html
import dash_bootstrap_components as dbc
from flask import session

def Navbar(title, date_label1='', date_label2='', date_label3=''):
    # Check if the session has a 'username'
    username = session.get('username')

    # Return a blank Div if no session
    if username is None:
        return html.Div()

    # Return the Navbar with session details if 'username' is in the session
    return html.Nav(
        className='navbar navbar-light bg-white',
        children=[
            html.Div(
                className='container',
                children=[
                    html.A(
                        href='#',
                        className='navbar-brand',
                        children=[
                            html.Img(id='download', src='/assets/image.png', alt='Download')
                        ]
                    ),
                    html.H1(title, className='word'),
                    # Removed the Time Period section
                    html.Label(username),
                    dbc.Button('Log out', id='logoutbutton', n_clicks=0)
                ]
            )
        ]
    )

