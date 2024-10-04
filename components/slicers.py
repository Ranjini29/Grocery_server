from dash import dcc, html

def create_slicers(year_options, month_options, category_options, item_options, supplier_options, pds_options, district_options):
    # Define common style for dropdowns
    dropdown_style = {
        'width': '100%',
        'padding': '4px',
        'font-size': '10px',
        'border': '1px solid #ccc',
        'border-radius': '3px',
        'box-sizing': 'border-box',
        'background-color': '#f8f9fa'
    }

    # Define common style for label
    label_style = {
        'display': 'block',
        'font-weight': 'bold',
        'margin-bottom': '3px',
        'font-size': '10px',
        'color': '#343a40'
    }

    # Container style for each slicer
    slicer_container_style = {
        'flex': '1',
        'margin-right': '5px',
        'margin-bottom': '5px',
        'min-width': '130px',
        'max-width': '150px',
        'position': 'relative'
    }

    # List of slicers with their labels, ids, and options
    slicers = [
        ('Year', 'year-slicer', year_options),
        ('Month', 'month-slicer', month_options),
        ('Product Category', 'product-category', category_options),
        ('Product Item', 'product-item', item_options),
        ('Supplier', 'supplier-name', supplier_options),
        ('PDS & Non PDS', 'pds-name', pds_options),
        ('District', 'district-name', district_options)
    ]

    # Create a Div containing all slicers, styled with flexbox
    return html.Div([
        html.Div([
            html.Label(label, style=label_style),
            dcc.Dropdown(
                id=id,
                options=[{'label': opt, 'value': opt} for opt in options],
                value=[],
                multi=True,
                style=dropdown_style
            )
        ], style=slicer_container_style) for label, id, options in slicers
    ], style={
        'display': 'flex',
        'flex-wrap': 'wrap',
        'justify-content': 'start',
        'padding': '10px',
        'background-color': '#ffffff',
        'border': '1px solid #ddd',
        'border-radius': '4px',
        'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'
    })
