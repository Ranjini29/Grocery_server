import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


def create_heatmap(df):
    """Create a heatmap from the given DataFrame and return a Plotly figure."""
    # Map months to their respective numbers for sorting
    month_order = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    
    # Create a Month_Number column for filtering and sorting
    df['Month_Number'] = df['Month'].map(month_order)

    # Sort by Year and Month_Number
    df.sort_values(by=['Year', 'Month_Number'], inplace=True)

    # Filter to include only the first 6 months (January to June)
    first_six_months = df[df['Month_Number'].isin([1, 2, 3,4,5,6,7,8,9,10,11,12])]

    # Group by Product Category and Month, summing the Resale Value
    heatmap_data = first_six_months.groupby(['Product Category', 'Month'])['Resale Value'].sum().reset_index()

    # Limit to the first 10 unique Product Categories
    limited_categories = heatmap_data['Product Category'].unique()[:10]
    heatmap_data = heatmap_data[heatmap_data['Product Category'].isin(limited_categories)]

    # Pivot the DataFrame to get Product Categories as rows and Month as columns
    heatmap_pivot = heatmap_data.pivot(index='Product Category', columns='Month', values='Resale Value').fillna(0)

    # Prepare data for the heatmap
    heatmap_array = heatmap_pivot.values  # 2D array for the heatmap
    row_labels = heatmap_pivot.index.tolist()  # Product Categories
    col_labels = heatmap_pivot.columns.tolist()  # Month

    # Create Plotly figure
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_array,
        x=col_labels,
        y=row_labels,
        colorscale=[[0, '#EDADAD'], [0.5, 'yellow'], [1, 'green']],  # Green to Yellow to Red colorscale
        text=heatmap_array,  # Show values in the heatmap
        hoverinfo='text'  # Show text on hover
    ))

    # Update layout
    fig.update_layout(
        yaxis_title="Product Category",
       height=900,
       width=900,
    )

    # Customize x-axis labels to be at the top
    fig.update_xaxes(tickangle=45, title_standoff=10)  # Rotate x-axis labels and adjust spacing

    # Add annotations for the heatmap values
    for i in range(len(row_labels)):
        for j in range(len(col_labels)):
            fig.add_annotation(
                x=col_labels[j],  # Month
                y=row_labels[i],  # Product Category
                text=f"{heatmap_array[i][j]:.1f}",  # Format the value
                showarrow=False,
                font=dict(color="black", size=10),  # Adjust font size
                xref="x",
                yref="y"
            )

    return fig
def create_donut_chart(df):
    """Create a donut chart from the given DataFrame and return a Plotly figure."""
    donut_data = df.groupby("PDS & Non PDS")["Resale Value"].sum().reset_index()
    donut_data = donut_data.sort_values(by='Resale Value', ascending=False)  # Sort in descending order

    fig = px.pie(donut_data, names='PDS & Non PDS', values='Resale Value', hole=0.5,
                 hover_data={'Resale Value': True, 'PDS & Non PDS': True})

    fig.update_traces(textinfo='percent + value')
    fig.update_layout(title_x=0.5,
                      legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5))

    return fig
