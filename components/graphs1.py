from dash import dash_table 
import pandas as pd
from dash.dash_table.Format import Group
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
# Suppress chained assignment warnings
pd.options.mode.chained_assignment = None  # default='warn'
standard_font_size = 14
axis_font_size = 10  # Smaller font size for x and y axes


def preprocess_data(df):
    if 'Resale Value' in df.columns and 'Cost Value' in df.columns:
        df['Profit Margin'] = df['Resale Value'] - df['Cost Value']
        df['Profit Margin%'] = (df['Profit Margin'] / df['Cost Value']) * 100
    else:
        df['Profit Margin'] = pd.NA
        df['Profit Margin%'] = pd.NA

    df['Profit Margin'] = df['Profit Margin'].round(2)
    df['Profit Margin%'] = df['Profit Margin%'].round(2)

    df['Parent_Category_ID'] = df['Product Category'].factorize()[0] + 1
    df['Product_Item_ID'] = df['Product Item'].factorize()[0] + 1

    return df
 

def create_parent_child_rows(df):
    # Aggregate parent rows
    parent_rows = df.groupby('Parent_Category_ID').agg({
        'Product Category': 'first',
        'Quantity': 'sum',
        'Resale Value': 'sum',
        'Profit Margin': 'sum',
        'Profit Margin%': 'mean'
    }).reset_index()

    # Aggregate child rows
    child_rows = df.groupby(['Product_Item_ID', 'Parent_Category_ID', 'Product Item']).agg({
        'Quantity': 'sum',
        'Resale Value': 'sum',
        'Profit Margin': 'sum',
        'Profit Margin%': 'mean'
    }).reset_index()

    return parent_rows, child_rows
def create_table(df):
    preprocessed_df = preprocess_data(df)
    parent_rows, child_rows = create_parent_child_rows(preprocessed_df)

    # Prepare parent data
    parent_data = parent_rows.to_dict('records')
    for row in parent_data:
        if pd.notna(row['Profit Margin%']):
            profit_margin_percentage = float(row['Profit Margin%'])
            row['Profit Margin%'] = f"{profit_margin_percentage:.1f}%"  # Format for display
        if pd.notna(row['Profit Margin']):
            row['Profit Margin'] = f"{row['Profit Margin']:.2f}"

    # Prepare child data similarly...
    child_data = child_rows.to_dict('records')
    for row in child_data:
        if pd.notna(row['Profit Margin%']):
            profit_margin_percentage = float(row['Profit Margin%'])
            row['Profit Margin%'] = f"{profit_margin_percentage:.1f}%"
        if pd.notna(row['Profit Margin']):
            row['Profit Margin'] = f"{row['Profit Margin']:.2f}"

    # Create parent table
    parent_table = dash_table.DataTable(
        id='parent-table',
        columns=[
            {'name': 'Product Category', 'id': 'Product Category'},
            {'name': 'Quantity', 'id': 'Quantity'},
            {'name': 'Resale Value', 'id': 'Resale Value'},
            {'name': 'Profit Margin', 'id': 'Profit Margin'},
            {'name': 'Profit Margin%', 'id': 'Profit Margin%'},
        ],
        data=parent_data,
        style_table={'overflowX': 'auto', 'height': '200px'},
        style_cell={'padding': '8px', 'textAlign': 'center'},
        page_action='native',
        page_size=10,
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_data={'whiteSpace': 'normal', 'height': 'auto'},
        style_data_conditional=[
            {
                'if': {
                    'column_id': 'Profit Margin%',
                    'filter_query': '{Profit Margin%} <= 10'
                },
                'color': 'red'  # Change font color to red
            },
            {
                'if': {
                    'column_id': 'Profit Margin%',
                    'filter_query': '{Profit Margin%} > 10'
                },
                'color': 'green'  # Change font color to green
            },
        ]
    )

    # Create child table
    child_table = dash_table.DataTable(
        id='child-table',
        columns=[
            {'name': 'Product Item', 'id': 'Product Item'},
            {'name': 'Quantity', 'id': 'Quantity'},
            {'name': 'Resale Value', 'id': 'Resale Value'},
            {'name': 'Profit Margin', 'id': 'Profit Margin'},
            {'name': 'Profit Margin%', 'id': 'Profit Margin%'},
        ],
        data=child_data,
        style_table={'overflowX': 'auto', 'height': '200px'},
        style_cell={'padding': '8px', 'textAlign': 'center'},
        page_action='native',
        page_size=10,
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_data={'whiteSpace': 'normal', 'height': 'auto'},
        style_data_conditional=[
            {
                'if': {
                    'column_id': 'Profit Margin%',
                    'filter_query': '{Profit Margin%} <= 10'
                },
                'color': 'red'  # Change font color to red
            },
            {
                'if': {
                    'column_id': 'Profit Margin%',
                    'filter_query': '{Profit Margin%} > 10'
                },
                'color': 'green'  # Change font color to green
            },
        ]
    )

    return html.Div([
        html.Div([
            html.H4("Product Category"),
            parent_table
        ]),
        html.Div([
            html.H4("Product Items"),
            child_table
        ])
    ])

def create_fifth_graph(filtered_data):
    """Create a bar graph for Product Category Profit Margin."""
    df5 = pd.DataFrame(filtered_data)

    if df5.empty or 'Resale Value' not in df5.columns or 'Cost Value' not in df5.columns:
        return dcc.Graph()  # Return an empty graph if necessary columns are missing or data is empty

    # Calculate Profit Margin
    df5['Profit Margin'] = df5['Resale Value'] - df5['Cost Value']

    # Aggregate by Product Category
    df5 = df5.groupby('Product Category').agg({'Profit Margin': 'sum'}).reset_index()
    df5.columns = ['Product Category', 'Profit Margin']
    top_categories = df5.nlargest(10, 'Profit Margin')

    bar_trace = go.Bar(
        x=top_categories['Profit Margin'],
        y=top_categories['Product Category'],
        orientation='h',
        marker_color='#D90515',
        text=top_categories['Profit Margin'],
        textposition='outside',
        texttemplate='%{text:.2s}',  # Use this format to show numbers with no decimal places
        textfont=dict(size=15, color='black')
    )

    fig5 = go.Figure(data=[bar_trace])
    fig5.update_layout(
        xaxis_title='Profit Margin',
        yaxis_title='Product Category',
        margin=dict(l=10, r=10, t=20, b=10),
        height=400,
        width=800,
        xaxis=dict(
            automargin=True,
            rangeslider=dict(visible=False),
            title_standoff=15,
            title_font=dict(size=axis_font_size),  # Set axis title font size
            tickfont=dict(size=axis_font_size)      # Set tick font size
        ),
        yaxis=dict(
            automargin=True,
            categoryorder='total ascending',
            title_font=dict(size=axis_font_size),  # Set axis title font size
            tickfont=dict(size=axis_font_size)      # Set tick font size
        )
    )
    fig5.update_traces(hovertemplate='Product Category: %{y}<br>Profit Margin: %{x}')

    return dcc.Graph(id='fifth-graph', figure=fig5, style={'height': '400px', 'width': '100%'}, config={'displayModeBar': True})

def create_sixth_graph(df):
    df = preprocess_data(df)

    if df.empty or 'Resale Value' not in df.columns or 'Cost Value' not in df.columns:
        return dcc.Graph()

    df['Profit Margin'] = df['Resale Value'] - df['Cost Value']
    df6 = df.groupby('Product Item').agg({'Profit Margin': 'sum'}).reset_index()
    top_items = df6.nlargest(10, 'Profit Margin')

    bar_trace = go.Bar(
        x=top_items['Profit Margin'],
        y=top_items['Product Item'],
        orientation='h',
        marker_color='#D90515',
        text=top_items['Profit Margin'],
        textposition='outside',
        texttemplate='%{text:.2s}',
        textfont=dict(size=15, color='black')
    )

    fig6 = go.Figure(data=[bar_trace])
    fig6.update_layout(
        xaxis_title='Profit Margin',
        yaxis_title='Product Item',
        margin=dict(l=10, r=10, t=20, b=10),
        height=400,
        width=800,
        xaxis=dict(
            automargin=True,
            rangeslider=dict(visible=False),
            title_standoff=15,
            title_font=dict(size=axis_font_size),  # Set axis title font size
            tickfont=dict(size=axis_font_size)      # Set tick font size
        ),
        yaxis=dict(
            automargin=True,
            categoryorder='total ascending',
            title_font=dict(size=axis_font_size),  # Set axis title font size
            tickfont=dict(size=axis_font_size)      # Set tick font size
        )
    )
    fig6.update_traces(hovertemplate='Product Item: %{y}<br>Profit Margin: %{x}')

    return dcc.Graph(id='sixth-graph', figure=fig6, style={'height': '400px', 'width': '100%'}, config={'displayModeBar': True})
