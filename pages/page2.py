import dash
from dash import dcc, html, Input, Output
import pandas as pd
from flask import Flask, session
from components.slicers1 import create_slicers_page2
from components.cards1 import create_cards_page2
from components.graphs1 import (
    create_parent_child_rows,
    preprocess_data,
    create_table,
    create_fifth_graph,
    create_sixth_graph,
)

def create_page2_layout(df):
    """Create the layout for Page 2 of the application."""
    return html.Div([
        # Slicers
        html.Div(
            create_slicers_page2(
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
            id='cards-container_page2',
            style={'display': 'flex', 'flex-wrap': 'wrap', 'padding': '10px'}
        ),
        # Combined Table
        html.Div(
            id='combined-table-container',
            style={'width': '100%', 'padding': '10px'}
        ),
        # Graphs Layout
        html.Div([
            html.Div([
                html.Div("Product Category - Profit Margin", className="card-headerline", style={
                    'background-color': '#070707',
                    'padding': '5px',
                    'border-bottom': '1px solid #ddd',
                    'font-weight': 'bold',
                    'color': '#fff',
                    'font-size': '14px',  # Adjust the font size here
                            'width': '100%', # Adjust the width as needed
                            'border-radius': '8px 8px 0 0',  # Curved corners at the top
                            'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'
                }),
                dcc.Graph(id='second-graph_page2', style={'width': '100%', 'padding': '10px', 'overflow': 'auto'})
            ], className="col-lg-6 mb-4"),
            html.Div([
                html.Div("Product Item - Profit Margin", className="card-headerbar", style={
                    'background-color': '#070707',
                    'padding': '5px',
                    'border-bottom': '1px solid #ddd',
                    'font-weight': 'bold',
                    'color': '#fff',
                    'font-size': '14px',  # Adjust the font size here
                     'width': '100%', # Adjust the width as needed
                     'border-radius': '8px 8px 0 0',  # Curved corners at the top
                     'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'
                }),
                dcc.Graph(id='third-graph_page2', style={'width': '100%', 'padding': '10px', 'overflow': 'auto'})
            ], className="col-lg-6 mb-4")
        ], className="row"),
    ])

def register_page2_callbacks(app, df):
    """Register callbacks for Page 2."""
    @app.callback(
        [Output('cards-container_page2', 'children'),
         Output('combined-table-container', 'children'),
         Output('second-graph_page2', 'figure'),
         Output('third-graph_page2', 'figure'),
         Output('year-slicer-page2', 'options'),
         Output('month-slicer-page2', 'options'),
         Output('product-category-page2', 'options'),
         Output('item-page2', 'options'),
         Output('supplier-page2', 'options'),
         Output('pds-page2', 'options'),
         Output('district-page2', 'options')],
        [Input('year-slicer-page2', 'value'),
         Input('month-slicer-page2', 'value'),
         Input('product-category-page2', 'value'),
         Input('item-page2', 'value'),
         Input('supplier-page2', 'value'),
         Input('pds-page2', 'value'),
         Input('district-page2', 'value')]
    )
    def update_content_page2(years, months, categories, items, suppliers, pds, districts):
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
                return [], [], {}, {}, [], [], [], [], [], [], []

            # Create cards
            cards = create_cards_page2(filtered_df)

            # Create the combined table with both parent and child rows
            combined_table = create_table(filtered_df)

            # Create graphs
            graph1 = create_fifth_graph(filtered_df)
            graph2 = create_sixth_graph(filtered_df)

            # Update slicer options based on filtered data
            year_options = [{'label': str(year), 'value': year} for year in filtered_df['Year'].unique()]
            month_options = [{'label': str(month), 'value': month} for month in filtered_df['Month'].unique()]
            category_options = [{'label': category, 'value': category} for category in filtered_df['Product Category'].unique()]
            item_options = [{'label': item, 'value': item} for item in filtered_df['Product Item'].unique()]
            supplier_options = [{'label': supplier, 'value': supplier} for supplier in filtered_df['Supplier'].unique()]
            pds_options = [{'label': pds_val, 'value': pds_val} for pds_val in filtered_df['PDS & Non PDS'].unique()]
            district_options = [{'label': district, 'value': district} for district in filtered_df['District'].unique()]

            return cards, combined_table, graph1.figure, graph2.figure, year_options, month_options, category_options, item_options, supplier_options, pds_options, district_options

        except Exception as e:
            print(f"Error in update_content_page2 callback: {e}")
            return [], [], {}, {}, [], [], [], [], [], [], []
