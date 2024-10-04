import plotly.graph_objects as go
import pandas as pd
from dash import dcc, html

# Define chart styles
chartline_style = {
    'border': '1px solid #ddd',
    'border-radius': '5px',
    'box-shadow': '0 4px 8px rgba(0,0,0,0.2)',
    'background-color': '#fff',
    'overflow-x': 'auto'
}

# Set a standard font size for main text and smaller sizes for axes
standard_font_size = 14
axis_font_size = 10  # Smaller font size for x and y axes

def create_first_graph(filtered_data):
    if filtered_data.empty:
        return html.Div("No data available for the selected filters.", style={'padding': '10px'})

    filtered_data['Profit Margin'] = (
        (filtered_data['Resale Value'] - filtered_data['Cost Value']) / filtered_data['Cost Value']
    ).fillna(0) * 100

    aggregated_data = filtered_data.groupby('Month_Year').agg(
        Cost_Value_Sum=pd.NamedAgg(column='Cost Value', aggfunc='sum'),
        Profit_Margin_Avg=pd.NamedAgg(column='Profit Margin', aggfunc='mean')
    ).reset_index()

    bar_trace = go.Bar(
        x=aggregated_data['Month_Year'],
        y=aggregated_data['Cost_Value_Sum'],
        name='Cost Value',
        marker_color='#D90515',
        text=aggregated_data['Cost_Value_Sum'],
        textposition='outside'
    )

    line_trace = go.Scatter(
        x=aggregated_data['Month_Year'],
        y=aggregated_data['Profit_Margin_Avg'],
        name='Profit Margin',
        mode='lines+markers+text',
        line=dict(color='darkblue'),
        marker=dict(size=8, color='darkblue'),
        text=aggregated_data['Profit_Margin_Avg'].apply(lambda x: f'{x:.2f}%'),
        texttemplate='%{text}',
        textposition='top right',
        yaxis='y2'
    )

    fig1 = go.Figure(data=[bar_trace, line_trace])
    fig1.update_layout(
        xaxis_title='Month Year',
        yaxis_title='Cost Value',
        yaxis2=dict(
            title='Profit Margin (%)',
            overlaying='y',
            side='right'
        ),
        margin=dict(l=10, r=10, t=20, b=40),
        xaxis=dict(
            tickmode='linear',
            tickangle=-45,
            title_font=dict(size=axis_font_size),  # Set smaller axis title font size
            tickfont=dict(size=axis_font_size)     # Set smaller axis tick font size
        ),
        height=450,
        width=700,
        legend=dict(x=0, y=1.15, orientation='h'),
        font=dict(size=standard_font_size)  # Set standard font size for other texts
    )

    return dcc.Graph(id='first-graph', figure=fig1, style={'height': '400px', 'width': '100%'}, config={'displayModeBar': True})

def create_second_graph(filtered_data):
    if filtered_data.empty:
        return html.Div("No data available for the selected filters.", style={'padding': '10px'})

    df2 = filtered_data.groupby('Supplier').agg({'Cost Value': 'sum'}).reset_index()
    df2.columns = ['Supplier', 'Cost Value']
    top_suppliers = df2.nlargest(10, 'Cost Value')

    bar_trace = go.Bar(
        x=top_suppliers['Cost Value'],
        y=top_suppliers['Supplier'],
        orientation='h',
        marker_color='#D90515',
        text=top_suppliers['Cost Value'],
        textposition='outside',
        texttemplate='%{text:.2s}',
        textfont=dict(size=15, color='black')
    )

    fig2 = go.Figure(data=[bar_trace])
    fig2.update_layout(
        xaxis_title='Cost Value',
        yaxis_title='Supplier',
        margin=dict(l=10, r=10, t=20, b=10),
        height=400,
        width=800,
        xaxis=dict(
            automargin=True,
            rangeslider=dict(visible=False),
            title_standoff=15,
            title_font=dict(size=axis_font_size),  # Set smaller axis title font size
            tickfont=dict(size=axis_font_size)     # Set smaller axis tick font size
        ),
        yaxis=dict(
            automargin=True,
            categoryorder='total ascending',
            title_font=dict(size=axis_font_size),  # Set smaller axis title font size
            tickfont=dict(size=axis_font_size)      # Set smaller axis tick font size
        ),
        font=dict(size=standard_font_size)  # Set standard font size for other texts
    )
    fig2.update_traces(hovertemplate='Supplier: %{y}<br>Cost Value: %{x}')

    return dcc.Graph(id='second-graph', figure=fig2, style={'height': '400px', 'width': '100%'}, config={'displayModeBar': True})

def create_third_graph(filtered_data):
    if filtered_data.empty:
        return html.Div("No data available for the selected filters.", style={'padding': '10px'})

    aggregated_data = filtered_data.groupby('Product Category').agg(
        Cost_Value_Sum=pd.NamedAgg(column='Cost Value', aggfunc='sum'),
        Resale_Value_Sum=pd.NamedAgg(column='Resale Value', aggfunc='sum')
    ).reset_index()
    top_categories = aggregated_data.nlargest(10, 'Cost_Value_Sum')

    cost_value_trace = go.Bar(
        y=top_categories['Product Category'],
        x=top_categories['Cost_Value_Sum'],
        name='Cost Value',
        orientation='h',
        marker_color='#D90515',
        text=top_categories['Cost_Value_Sum'],
        textposition='outside'
    )

    resale_value_trace = go.Bar(
        y=top_categories['Product Category'],
        x=top_categories['Resale_Value_Sum'],
        name='Resale Value',
        orientation='h',
        marker_color='black',
        text=top_categories['Resale_Value_Sum'],
        textposition='inside'
    )

    fig3 = go.Figure(data=[cost_value_trace, resale_value_trace])
    fig3.update_layout(
        barmode='group',
        xaxis_title='Value',
        yaxis_title='Product Category',
        margin=dict(l=10, r=10, t=60, b=40),
        height=400,
        width=700,
        xaxis=dict(
            automargin=True,
            title_font=dict(size=axis_font_size),  # Set smaller axis title font size
            tickfont=dict(size=axis_font_size)      # Set smaller axis tick font size
        ),
        yaxis=dict(
            automargin=True,
            categoryorder='total ascending',
            title_font=dict(size=axis_font_size),  # Set smaller axis title font size
            tickfont=dict(size=axis_font_size)      # Set smaller axis tick font size
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.1,
            xanchor='center',
            x=0.5
        ),
        font=dict(size=standard_font_size)  # Set standard font size for other texts
    )

    return dcc.Graph(id='third-graph', figure=fig3, style={'height': '400px', 'width': '100%'}, config={'displayModeBar': True})

def create_fourth_graph(filtered_data):
    if filtered_data.empty:
        return html.Div("No data available for the selected filters.", style={'padding': '10px'})

    df4 = filtered_data.groupby('Product Item').agg({'Cost Value': 'sum'}).reset_index()
    df4.columns = ['Product Item', 'Cost Value']
    top_items = df4.nlargest(10, 'Cost Value')

    bar_trace = go.Bar(
        x=top_items['Cost Value'],
        y=top_items['Product Item'],
        orientation='h',
        marker_color='#D90515',
        text=top_items['Cost Value'],
        textposition='inside',
        texttemplate='%{text:.2s}',
        textfont=dict(size=15, color='black')
    )

    fig4 = go.Figure(data=[bar_trace])
    fig4.update_layout(
        xaxis_title='Cost Value',
        yaxis_title='Product Item',
        margin=dict(l=10, r=10, t=20, b=10),
        height=400,
        width=700,
        xaxis=dict(
            rangeslider=dict(visible=False),
            title_standoff=15,
            title_font=dict(size=axis_font_size),  # Set smaller axis title font size
            tickfont=dict(size=axis_font_size)      # Set smaller axis tick font size
        ),
        yaxis=dict(
            categoryorder='total ascending',
            title_font=dict(size=axis_font_size),  # Set smaller axis title font size
            tickfont=dict(size=axis_font_size)      # Set smaller axis tick font size
        ),
font=dict(size=standard_font_size)  # Set standard font size for other texts
    )
    fig4.update_traces(hovertemplate='Product Item: %{y}<br>Cost Value: %{x}')

    return dcc.Graph(id='fourth-graph', figure=fig4, style={'height': '400px', 'width': '100%'}, config={'displayModeBar': True})