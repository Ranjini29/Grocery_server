import dash_bootstrap_components as dbc
from dash import html

def create_cards(filtered_data):
    # Print column names to check
    print(filtered_data.columns)
    
    # Check if required columns are in the DataFrame
    required_columns = ['Transactions', 'Quantity', 'Cost Value', 'Resale Value']
    for col in required_columns:
        if col not in filtered_data.columns:
            raise ValueError(f"Missing required column: {col}")

    # Extract data from the filtered DataFrame
    transactions = filtered_data['Transactions'].tolist()
    quantities = filtered_data['Quantity'].astype(float).tolist()  # Convert to float if needed
    costs = filtered_data['Cost Value'].astype(float).tolist()  # Convert to float if needed
    sales = filtered_data['Resale Value'].astype(float).tolist()  # Convert to float if needed

    # Calculate the required metrics
    total_transactions = len(transactions)
    total_quantity = sum(quantities)
    total_cost = sum(costs)
    total_sales = sum(sales)
    profit = total_sales - total_cost

    # Define card information
    cards_info = [
        {'id': 'card-1', 'header': 'Transactions', 'body': str(total_transactions), 'style': {'background-color': '#007bff', 'color': '#fff'}},
        {'id': 'card-2', 'header': 'Quantity', 'body': str(total_quantity), 'style': {'background-color': '#6c757d', 'color': '#fff'}},
        {'id': 'card-3', 'header': 'Cost', 'body': f'INR {total_cost:.2f}', 'style': {'background-color': '#28a745', 'color': '#fff'}},
        {'id': 'card-4', 'header': 'Sales', 'body': f'INR {total_sales:.2f}', 'style': {'background-color': '#ffc107', 'color': '#fff'}},
        {'id': 'card-5', 'header': 'Profit', 'body': f'INR {profit:.2f}', 'style': {'background-color': '#dc3545', 'color': '#fff'}}
    ]

    card_header_style = {
        'font-size': '15px',
        'font-weight': 'bold'
    }
    
    card_body_style = {
        'font-size': '14px'
    }

    # Create the cards using Dash Bootstrap Components
    cards = [
        html.Div(
            dbc.Card(
                [
                    dbc.CardHeader(info['header'], style=card_header_style),
                    dbc.CardBody(
                        html.P(info['body'], id=info['id'], style=card_body_style)
                    ),
                ],
                style=info['style'],
            ),
            style={
                'flex': '1 1 auto',  # Allow the cards to grow and shrink based on available space
                'margin': '10px',
                'min-width': '180px',  # Ensure a minimum width to avoid too small cards
            }
        )
        for info in cards_info
    ]

    return html.Div(
        cards,
        style={
            'display': 'flex',
            'flex-wrap': 'nowrap',  # Prevent wrapping, keep all cards in a single row
            'justify-content': 'flex-start',  # Align cards to the start
            'overflow-x': 'hidden',  # Add horizontal scrolling if cards overflow
        }
    )
