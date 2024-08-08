import os
from pyngrok import ngrok
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Load and clean the data
file_path = os.path.join(os.path.dirname(__file__), 'HARVERST.xlsx')
data_clean = pd.read_excel(file_path, header=1)
data_clean = data_clean[['Region', 'District', 'FBA Name', "DAC's Name", 'Amount of seed supplied in kgs', 'Harvest status', 'Threshing status', 'Harvested in Kgs']]
data_clean.columns = ['Region', 'District', 'FBA_Name', 'DAC_Name', 'Seeds_Used_in_Kgs', 'Harvest_Status', 'Threshing_Status', 'Harvest_Amount_in_Kgs']
data_clean = data_clean.dropna(subset=['Region', 'District', 'FBA_Name', 'DAC_Name'])
data_clean['Seeds_Used_in_Kgs'] = pd.to_numeric(data_clean['Seeds_Used_in_Kgs'], errors='coerce').fillna(0)
data_clean['Harvest_Amount_in_Kgs'] = pd.to_numeric(data_clean['Harvest_Amount_in_Kgs'], errors='coerce').fillna(0)

# Standardize the status values
data_clean['Harvest_Status'] = data_clean['Harvest_Status'].apply(lambda x: 'DONE' if x == 'DONE' else 'NOT YET')
data_clean['Threshing_Status'] = data_clean['Threshing_Status'].apply(lambda x: 'DONE' if x == 'DONE' else 'NOT YET')

# Initialize the Dash app with suppress_callback_exceptions
app = Dash(__name__, suppress_callback_exceptions=True)

# Define the layout of the app
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Common header layout with navigation links
header_layout = html.Div([
    html.H1("Agent Performance Dashboard", style={'text-align': 'center', 'background-color': '#387F39', 'color': 'white', 'padding': '10px'}),
    html.Div([
        dcc.Link(html.Button('Home', style={'margin-right': '10px', 'background-color': '#387F39', 'color': 'white', 'border': 'none', 'padding': '10px'}), href='/'),
        dcc.Link(html.Button('DAC Performance', style={'background-color': '#387F39', 'color': 'white', 'border': 'none', 'padding': '10px'}), href='/dac-performance'),
    ], style={'text-align': 'center', 'padding': '10px'}),
])

# Layout for the FBA performance page
fba_layout = html.Div([
    header_layout,
    
    html.Div([
        html.Label("Select Region:"),
        dcc.Dropdown(
            id='region-dropdown',
            options=[{'label': region, 'value': region} for region in data_clean['Region'].unique()],
            value=data_clean['Region'].unique().tolist(),
            multi=True
        ),
    ]),

    html.Div([
        html.Label("Select District:"),
        dcc.Dropdown(
            id='district-dropdown',
            options=[{'label': district, 'value': district} for district in data_clean['District'].unique()],
            value=data_clean['District'].unique().tolist(),
            multi=True
        ),
    ]),
    
    dcc.Graph(id='harvest-amount-graph'),
    dcc.Graph(id='seeds-used-graph'),
    
    html.Div([
        html.Label("Harvest Status:"),
        dcc.Dropdown(
            id='harvest-status-dropdown',
            options=[{'label': status, 'value': status} for status in data_clean['Harvest_Status'].unique()],
            value=data_clean['Harvest_Status'].unique().tolist(),
            multi=True
        ),
    ]),
    
    html.Div([
        html.Label("Threshing Status:"),
        dcc.Dropdown(
            id='threshing-status-dropdown',
            options=[{'label': status, 'value': status} for status in data_clean['Threshing_Status'].unique()],
            value=data_clean['Threshing_Status'].unique().tolist(),
            multi=True
        ),
    ]),
    
    dcc.Graph(id='harvest-status-graph'),
    dcc.Graph(id='threshing-status-graph'),
])

# Layout for the DAC performance page
dac_layout = html.Div([
    header_layout,
    
    html.Div([
        html.Label("Select FBA:"),
        dcc.Dropdown(
            id='dac-fba-dropdown',
            options=[{'label': fba, 'value': fba} for fba in data_clean['FBA_Name'].unique()],
            value=data_clean['FBA_Name'].unique().tolist(),
            multi=True
        ),
    ]),
    
    dcc.Graph(id='dac-harvest-amount-graph'),
    dcc.Graph(id='dac-seeds-used-graph'),
    
    html.Div([
        html.Label("Harvest Status:"),
        dcc.Dropdown(
            id='dac-harvest-status-dropdown',
            options=[{'label': status, 'value': status} for status in data_clean['Harvest_Status'].unique()],
            value=data_clean['Harvest_Status'].unique().tolist(),
            multi=True
        ),
    ]),
    
    html.Div([
        html.Label("Threshing Status:"),
        dcc.Dropdown(
            id='dac-threshing-status-dropdown',
            options=[{'label': status, 'value': status} for status in data_clean['Threshing_Status'].unique()],
            value=data_clean['Threshing_Status'].unique().tolist(),
            multi=True
        ),
    ]),
    
    dcc.Graph(id='dac-harvest-status-graph'),
    dcc.Graph(id='dac-threshing-status-graph'),
])

# Define the callback to update the graphs on the FBA performance page
@app.callback(
    [Output('harvest-amount-graph', 'figure'),
     Output('seeds-used-graph', 'figure'),
     Output('harvest-status-graph', 'figure'),
     Output('threshing-status-graph', 'figure')],
    [Input('region-dropdown', 'value'),
     Input('district-dropdown', 'value'),
     Input('harvest-status-dropdown', 'value'),
     Input('threshing-status-dropdown', 'value')]
)
def update_fba_graphs(selected_regions, selected_districts, selected_harvest_status, selected_threshing_status):
    filtered_data = data_clean[(data_clean['Region'].isin(selected_regions)) &
                               (data_clean['District'].isin(selected_districts)) &
                               (data_clean['Harvest_Status'].isin(selected_harvest_status)) &
                               (data_clean['Threshing_Status'].isin(selected_threshing_status))]
    
    # Harvest Amount in Kgs
    harvest_amount_fig = px.bar(
        filtered_data, x='FBA_Name', y='Harvest_Amount_in_Kgs', color='Region',
        labels={'Harvest_Amount_in_Kgs': 'Harvest Amount (Kgs)'},
        title='Harvest Amount in Kgs'
    )
    
    # Seeds Used in Kgs
    seeds_used_fig = px.bar(
        filtered_data, x='FBA_Name', y='Seeds_Used_in_Kgs', color='Region',
        labels={'Seeds_Used_in_Kgs': 'Seeds Used (Kgs)'},
        title='Seeds Used in Kgs'
    )
    
    # Harvest Status
    harvest_status_fig = px.scatter(
        filtered_data, x='FBA_Name', y='Harvest_Amount_in_Kgs', color='Harvest_Status',
        size='Seeds_Used_in_Kgs', hover_data=['Threshing_Status'],
        labels={'Harvest_Amount_in_Kgs': 'Harvest Amount (Kgs)', 'Seeds_Used_in_Kgs': 'Seeds Used (Kgs)'},
        title='Harvest Status'
    )
    
    # Threshing Status
    threshing_status_fig = px.scatter(
        filtered_data, x='FBA_Name', y='Harvest_Amount_in_Kgs', color='Threshing_Status',
        size='Seeds_Used_in_Kgs', hover_data=['Harvest_Status'],
        labels={'Harvest_Amount_in_Kgs': 'Harvest Amount (Kgs)', 'Seeds_Used_in_Kgs': 'Seeds Used (Kgs)'},
        title='Threshing Status'
    )
    
    return harvest_amount_fig, seeds_used_fig, harvest_status_fig, threshing_status_fig

# Define the callback to update the graphs on the DAC performance page
@app.callback(
    [Output('dac-harvest-amount-graph', 'figure'),
     Output('dac-seeds-used-graph', 'figure'),
     Output('dac-harvest-status-graph', 'figure'),
     Output('dac-threshing-status-graph', 'figure')],
    [Input('dac-fba-dropdown', 'value'),
     Input('dac-harvest-status-dropdown', 'value'),
     Input('dac-threshing-status-dropdown', 'value')]
)
def update_dac_graphs(selected_fbas, selected_harvest_status, selected_threshing_status):
    filtered_data = data_clean[(data_clean['FBA_Name'].isin(selected_fbas)) &
                               (data_clean['Harvest_Status'].isin(selected_harvest_status)) &
                               (data_clean['Threshing_Status'].isin(selected_threshing_status))]
    
        # Harvest Amount in Kgs
    harvest_amount_fig = px.bar(
        filtered_data, x='DAC_Name', y='Harvest_Amount_in_Kgs', color='Region',
        labels={'Harvest_Amount_in_Kgs': 'Harvest Amount (Kgs)'},
        title='Harvest Amount in Kgs'
    )
    
    # Seeds Used in Kgs
    seeds_used_fig = px.bar(
        filtered_data, x='DAC_Name', y='Seeds_Used_in_Kgs', color='Region',
        labels={'Seeds_Used_in_Kgs': 'Seeds Used (Kgs)'},
        title='Seeds Used in Kgs'
    )
    
    # Harvest Status
    harvest_status_fig = px.scatter(
        filtered_data, x='DAC_Name', y='Harvest_Amount_in_Kgs', color='Harvest_Status',
        size='Seeds_Used_in_Kgs', hover_data=['Threshing_Status'],
        labels={'Harvest_Amount_in_Kgs': 'Harvest Amount (Kgs)', 'Seeds_Used_in_Kgs': 'Seeds Used (Kgs)'},
        title='Harvest Status'
    )
    
    # Threshing Status
    threshing_status_fig = px.scatter(
        filtered_data, x='DAC_Name', y='Harvest_Amount_in_Kgs', color='Threshing_Status',
        size='Seeds_Used_in_Kgs', hover_data=['Harvest_Status'],
        labels={'Harvest_Amount_in_Kgs': 'Harvest Amount (Kgs)', 'Seeds_Used_in_Kgs': 'Seeds Used (Kgs)'},
        title='Threshing Status'
    )
    
    return harvest_amount_fig, seeds_used_fig, harvest_status_fig, threshing_status_fig

# Update the page content based on the URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/':
        return fba_layout
    elif pathname == '/dac-performance':
        return dac_layout
    else:
        return '404'

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

