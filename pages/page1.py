import dash
from dash import dcc, html, Input, Output
import pandas as pd
from flask import Flask, session
from flask_session import Session
from components.slicers import create_slicers
from components.cards import create_cards
from components.graphs import (
    create_first_graph,
    create_second_graph,
    create_third_graph,
    create_fourth_graph
)

def create_page1(df):
    """
    Create the layout for Page 1 of the application with updated graph layout.
    """
    return html.Div([
        # Slicers
        html.Div(
            create_slicers(
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
            id='cards-container',
             className="row",
            style={'display': 'flex', 'flex-wrap': 'wrap', 'padding': '10px'}
        ),

        # Graphs Layout
        html.Div([
            # First Row: First and Second Graphs
            html.Div(className="row", style={'margin': '10px 0'}, children=[
                html.Div(className="col-lg-6 col-md-12 mb-4", children=[
                    html.Div(
                        "Monthly Analysis: Purchase vs Profit",
                        className="card-headerline",
                        style={
                            'background-color': '#070707',
                            'padding': '4px',
                            'border-bottom': '1px solid #ddd',
                            'font-weight': 'bold',
                            'color': '#fff',
                            'font-size': '14px',
                            'width': '100%',
                            'border-radius': '8px 8px 0 0',
                            'box-shadow': '0 2px 4px rgba(0,0,0,0.1)' 
                        }
                    ),
                    html.Div(id='first-second-graphs-container', style={'width': '100%', 'padding': '10px', 'overflow': 'auto'})
                ]),

                html.Div(className="col-lg-6 col-md-12 mb-4", children=[
                    html.Div(
                        "Top Supplier - Purchase",
                        className="card-headerbar",
                        style={
                            'background-color': '#070707',
                            'padding': '4px',
                            'border-bottom': '1px solid #ddd',
                            'font-weight': 'bold',
                            'color': '#fff',
                            'font-size': '14px',
                            'width': '100%',
                            'border-radius': '8px 8px 0 0',
                            'box-shadow': '0 2px 4px rgba(0,0,0,0.1)' 
                        }
                    ),
                    html.Div(id='second-graph-container', style={'width': '100%', 'padding': '10px', 'overflow': 'auto'})
                ])
            ]),

            # Second Row: Third and Fourth Graphs
            html.Div(className="row", style={'margin': '10px 0'}, children=[
                html.Div(className="col-lg-6 col-md-12 mb-4", children=[
                    html.Div(
                        "Product Category - Purchase vs Sales",
                        className="card-headerbar",
                        style={
                            'background-color': '#070707',
                            'padding': '4px',
                            'border-bottom': '1px solid #ddd',
                            'font-weight': 'bold',
                            'color': '#fff',
                            'font-size': '14px',
                            'width': '100%',
                            'border-radius': '8px 8px 0 0',
                            'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'
                        }
                    ),
                    html.Div(id='third-graph-container', style={'width': '100%', 'padding': '10px', 'overflow': 'auto'})
                ]),

                html.Div(className="col-lg-6 col-md-12 mb-4", children=[
                    html.Div(
                        "Product Item - Purchase Analysis",
                        className="card-headerbar",
                        style={
                            'background-color': '#070707',
                            'padding': '4px',
                            'border-bottom': '1px solid #ddd',
                            'font-weight': 'bold',
                            'color': '#fff',
                            'font-size': '14px',
                            'width': '100%',
                            'border-radius': '8px 8px 0 0',
                            'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'
                        }
                    ),
                    html.Div(id='fourth-graph-container', style={'width': '100%', 'padding': '10px', 'overflow': 'auto'})
                ])
            ]),
        ])
    ])


def register_callbacks(app, df):
    """
    Register callbacks for Page 1.
    """
    @app.callback(
        [Output('cards-container', 'children'),
         Output('first-second-graphs-container', 'children'),
         Output('second-graph-container', 'children'),
         Output('third-graph-container', 'children'),
         Output('fourth-graph-container', 'children'),
         Output('year-slicer', 'options'),
         Output('month-slicer', 'options'),
         Output('product-category', 'options'),
         Output('product-item', 'options'),
         Output('supplier-name', 'options'),
         Output('pds-name', 'options'),
         Output('district-name', 'options')],
        [Input('year-slicer', 'value'),
         Input('month-slicer', 'value'),
         Input('product-category', 'value'),
         Input('product-item', 'value'),
         Input('supplier-name', 'value'),
         Input('pds-name', 'value'),
         Input('district-name', 'value')]
    )
    def update_content(years, months, categories, items, suppliers, pds, districts):
        try:
            # Get the district from the session
            session_district = session.get('district')
            # Initialize the filter condition to True for all rows
            filter_condition = pd.Series([True] * len(df))

            # Apply filters based on selected values
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

            # Filter the DataFrame based on the filter condition
            filtered_data = df[filter_condition]

            # Generate cards using the existing function
            cards = create_cards(filtered_data)

            # Generate graphs using the existing functions
            first_graph = create_first_graph(filtered_data)
            second_graph = create_second_graph(filtered_data)
            third_graph = create_third_graph(filtered_data)
            fourth_graph = create_fourth_graph(filtered_data)

            # Update slicer options based on filtered data
            year_options = [{'label': str(year), 'value': year} for year in filtered_data['Year'].unique()]
            month_options = [{'label': month, 'value': month} for month in filtered_data['Month'].unique()]
            category_options = [{'label': category, 'value': category} for category in filtered_data['Product Category'].unique()]
            item_options = [{'label': item, 'value': item} for item in filtered_data['Product Item'].unique()]
            supplier_options = [{'label': supplier, 'value': supplier} for supplier in filtered_data['Supplier'].unique()]
            pds_options = [{'label': pds_val, 'value': pds_val} for pds_val in filtered_data['PDS & Non PDS'].unique()]
            district_options = [{'label': district, 'value': district} for district in filtered_data['District'].unique()]

            # Return results including updated slicer options
            return (cards, [first_graph], [second_graph], [third_graph], [fourth_graph],
                    year_options, month_options, category_options, item_options, supplier_options, pds_options, district_options)

        except Exception as e:
            print(f"Error in update_content callback: {e}")
            return (
                [html.Div("An error occurred while generating cards.", style={'padding': '10px'})],
                [html.Div("An error occurred while generating the first graph.", style={'padding': '10px'})],
                [html.Div("An error occurred while generating the second graph.", style={'padding': '10px'})],
                [html.Div("An error occurred while generating the third graph.", style={'padding': '10px'})],
                [html.Div("An error occurred while generating the fourth graph.", style={'padding': '10px'})],
                [], [], [], [], [], [], []
            )

