import dash
from dash import dcc, html, Input, Output
import pandas as pd
from flask import Flask, session
from components.slicer2 import create_slicers_page3
from components.cards2 import create_cards_page3
from components.graphs3 import create_heatmap, create_donut_chart  # Import your graph functions

def create_page3_layout(df):
    """Create the layout for Page 3 of the application."""
    return html.Div([
        # Slicers
        html.Div(
            create_slicers_page3(
                year_options=df['Year'].unique(),
                month_options=df['Month'].unique(),
                category_options=df['Product Category'].unique(),
                item_options=df['Product Item'].unique(),
                supplier_options=df['Supplier'].unique(),
                pds_options=df['PDS & Non PDS'].unique(),
                district_options=df['District'].unique()
            ),
            style={'padding': '10px'}
        ),
        
        # Cards
        html.Div(
            id='cards-container_page3',
            style={'display': 'flex', 'flex-wrap': 'wrap', 'padding': '10px'}
        ),

        # Graphs Layout
        html.Div([
            html.Div([
                html.Div("Heat Map - Product Category", className="card-headerline", style={
                    'background-color': '#070707',
                    'padding': '5px',
                    'border-bottom': '1px solid #ddd',
                    'font-weight': 'bold',
                    'color': '#fff',
                    'font-size': '14px',  # Adjust the font size here
                    'width': '100%',
                    'border-radius': '8px 8px 0 0',  # Curved corners at the top
                    'box-shadow': '0 2px 4px rgba(0,0,0,0.1)' 
                }),
                html.Div(dcc.Graph(id='first_heatmap', style={'width': '100%', 'height': '400px'}), style={'overflow': 'auto', 'height': '400px'})
            ], className="col-lg-6 mb-4"),  # Use col-lg-6 for half width

            html.Div([
                html.Div("PDS & Non PDS - Sales", className="card-headerbar", style={
                    'background-color': '#070707',
                    'padding': '5px',
                    'border-bottom': '1px solid #ddd',
                    'font-weight': 'bold',
                    'color': '#fff',
                    'font-size': '14px',  # Adjust the font size here
                    'width': '100%',
                    'border-radius': '8px 8px 0 0',  # Curved corners at the top
                    'box-shadow': '0 2px 4px rgba(0,0,0,0.1)' 
                }),
                dcc.Graph(id='second-graph-container', style={'width': '100%', 'height': '400px'})
            ], className="col-lg-6 mb-4")  # Also make this half width
        ], className="row")  # Bootstrap row class to handle the layout
    ])


def register_page3_callbacks(app, df):
    """Register callbacks for Page 3."""
    @app.callback(
        [Output('cards-container_page3', 'children'),
         Output('first_heatmap', 'figure'),
         Output('second-graph-container', 'figure'),
         Output('year-slicer-page3', 'options'),
         Output('month-slicer-page3', 'options'),
         Output('product-category-page3', 'options'),
         Output('item-page3', 'options'),
         Output('supplier-page3', 'options'),
         Output('pds-page3', 'options'),
         Output('district-page3', 'options')],
        [Input('year-slicer-page3', 'value'),
         Input('month-slicer-page3', 'value'),
         Input('product-category-page3', 'value'),
         Input('item-page3', 'value'),
         Input('supplier-page3', 'value'),
         Input('pds-page3', 'value'),
         Input('district-page3', 'value')]
    )
    def update_content_page3(years, months, categories, items, suppliers, pds, districts):
        try:

            # Get the district from the session
            session_district = session.get('district')

            # Filter the DataFrame
            filter_condition = pd.Series([True] * len(df))
            if years:
                filter_condition &= df['Year'].isin(years)
            if months:
                filter_condition &= df['Month'].isin(months)
            if categories:
                filter_condition &= df['Product Category'].isin(categories)
            if items:
                filter_condition &= df['Product Item'].isin(items)
            if suppliers:
                filter_condition &= df['Supplier'].isin(suppliers)
            if pds:
                filter_condition &= df['PDS & Non PDS'].isin(pds)
            if districts:
                filter_condition &= df['District'].isin(districts)

            # Filter DataFrame based on session district if it exists
            if session_district:
                filter_condition &= df['District'] == session_district

            filtered_df = df[filter_condition]

            # Check if filtered DataFrame is empty
            if filtered_df.empty:
                return [], {}, {}, [], [], [], [], [], [], []

            # Create cards
            cards = create_cards_page3(filtered_df)

            # Create graphs
            heatmap_fig = create_heatmap(filtered_df)  # This should return a Plotly figure
            donut_fig = create_donut_chart(filtered_df)  # This should return a Plotly figure

            # Update slicer options based on the filtered DataFrame
            year_options = [{'label': str(year), 'value': year} for year in filtered_df['Year'].unique()]
            month_options = [{'label': month, 'value': month} for month in filtered_df['Month'].unique()]
            category_options = [{'label': category, 'value': category} for category in filtered_df['Product Category'].unique()]
            item_options = [{'label': item, 'value': item} for item in filtered_df['Product Item'].unique()]
            supplier_options = [{'label': supplier, 'value': supplier} for supplier in filtered_df['Supplier'].unique()]
            pds_options = [{'label': pds_item, 'value': pds_item} for pds_item in filtered_df['PDS & Non PDS'].unique()]
            district_options = [{'label': district, 'value': district} for district in filtered_df['District'].unique()]

            return cards, heatmap_fig, donut_fig, year_options, month_options, category_options, item_options, supplier_options, pds_options, district_options

        except Exception as e:
            print(f"Error in update_content_page3 callback: {e}")
            return [], {}, {}, [], [], [], [], [], [], []
