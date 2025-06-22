from dash import Dash, html, dash_table, dcc
import pandas as pd
import dash_leaflet as dl
import plotly.express as px
from dash.dependencies import Input, Output, State
import base64
import numpy as np
from AnimalShelter import AnimalShelter


# Connect to MongoDB using AnimalShelter class

animals = AnimalShelter()  
# Read animal data from the database
df = pd.DataFrame.from_records(animals.read({}))
if '_id' in df.columns:
    df.drop(columns=['_id'], inplace=True)

# Initialize Dash app
app = Dash()
image_filename = 'Grazioso Salvare Logo.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

# List of columns that should always be hidden in the DataTable
ALWAYS_HIDDEN = ['datetime', 'monthyear', 'outcome_subtype']

# Shared card style for the registration and login forms
card_style = {
    'backgroundColor': '#f9f9f9',
    'padding': '20px',
    'borderRadius': '8px',
    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
    'marginBottom': '20px',
    'width': '500px',
    'margin': '20px auto'
}

# Layout
app.layout = html.Div([
    dcc.Store(id='login-state', data={'logged_in': False, 'username': None}),
    # Register and Login Forms
    html.Div([
        # Registration Form
        html.Div([
        html.H3("Register User", style={'marginBottom': '10px'}),
        dcc.Input(
            id='reg-username',
            type='text',
            placeholder='Username',
            style={'marginRight': '10px', 'padding': '8px', 'width': '200px', 'borderRadius': '5px', 'border': '1px solid #ccc'}
        ),
        dcc.Input(
            id='reg-password',
            type='password',
            placeholder='Password',
            style={'marginRight': '10px', 'padding': '8px', 'width': '200px', 'borderRadius': '5px', 'border': '1px solid #ccc'}
        ),
        html.Button(
            'Register',
            id='register-btn',
            n_clicks=0,
            type = 'submit',
            style={'padding': '8px 16px', 'borderRadius': '5px', 'backgroundColor': '#007bff', 'color': 'white', 'border': 'none'}
        ),
        html.Div(id='register-message', style={'color': 'green', 'marginTop': '10px'})
    ], style=card_style),
    
    # Login form
    html.Div([
        html.H3("Login", style={'marginBottom': '10px'}),
        dcc.Input(
            id='login-username',
            type='text',
            placeholder='Username',
            style={'marginRight': '10px', 'padding': '8px', 'width': '200px', 'borderRadius': '5px', 'border': '1px solid #ccc'}
        ),
        dcc.Input(
            id='login-password',
            type='password',
            placeholder='Password',
            style={'marginRight': '10px', 'padding': '8px', 'width': '200px', 'borderRadius': '5px', 'border': '1px solid #ccc'}
        ),
        html.Button(
            'Login',
            id='login-btn',
            n_clicks=0,
            type='submit',
            style={'padding': '8px 16px', 'borderRadius': '5px', 'backgroundColor': '#28a745', 'color': 'white', 'border': 'none'}
        ),
        html.Div(id='login-message', style={'color': 'green', 'marginTop': '10px'})
    ], style=card_style),
]),
    # Message shown if not logged in
    html.Div(id='login-prompt'),
    html.Div(id='hidden-div', style={'display': 'none'}),
    # Main Dashboard Content
    html.Div(
        style={'textAlign': 'center'},
        children=[
            html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode())),
            html.B(html.H1('Agnieszka Sikora Animal Shelter'))
        ]
    ),
    html.Hr(),

    # Dropdown for filtering rescue types
    html.Div(
        className='row',
        children=[
            dcc.Dropdown(
                id='filter-type',
                options=[
                    {'label': 'Water Rescue', 'value': 'water'},
                    {'label': 'Mountain or Wilderness Rescue', 'value': 'mountain'},
                    {'label': 'Disaster Rescue or Individual Tracking', 'value': 'disaster'},
                    {'label': 'Reset', 'value': 'reset'}
                ],
                placeholder='Select a rescue type',
                clearable=False
            )
        ]
    ),

    # Toggle columns visibility and main content
    html.Div([
        html.Label("Toggle columns:"),
        dcc.Checklist(
            id='column-toggle',
            options=[
                {'label': col, 'value': col}
                for col in df.columns if col not in ALWAYS_HIDDEN
            ],
            value=[col for col in df.columns if col not in ALWAYS_HIDDEN],
            inline=True
        )
    ], style={'margin': '10px 0'}),

    # Protected content that is only visible when logged in
    html.Div(
    id='protected-content',
    children=[
        # DataTable for displaying animal data
        dash_table.DataTable(
            id='datatable-id',
            columns=[{'name': i, 'id': i, 'deletable': False, 'selectable': True} for i in df.columns],
            data=df.to_dict('records'),
            row_selectable='single',
            editable=False,
            sort_action='native',
            filter_action='native',
            selected_rows=[],
            selected_columns=[],
            column_selectable=False,
            row_deletable=False,
            page_action='native',
            page_current=0,
            page_size=10,
            hidden_columns=ALWAYS_HIDDEN
        ),
        html.Br(),
        html.Hr(),
        # Graphs and Map
        html.Div(
            className='row',
            style={'display': 'flex'},
            children=[
                html.Div(
                    id='graph-id',
                    className='col s12 m6'
                ),
                html.Div(
                    id='map-id',
                    className='col s12 m6'
                )
            ]
        )
    ]
)
]
                      )
# Callback to update the DataTable based on the selected rescue type
@app.callback(Output('datatable-id', 'data'),
              [Input('filter-type', 'value')])
def update_dashboard(filter_type):
    try:
        if filter_type == 'water':
            query = {
                'animal_type': 'Dog',
                'breed': {'$in': ['Labrador Retriever Mix', 'Chesapeake Bay Retriever', 'Newfoundland']},
                'sex_upon_outcome': 'Intact Female',
                'age_upon_outcome_in_weeks': {'$gte': 26, '$lte': 156}
            }
        elif filter_type == 'mountain':
            query = {
                'animal_type': 'Dog',
                'breed': {'$in': ['German Shepherd', 'Siberian Husky', 'Alaskan Malamute', 'Old English Sheepdog', 'Rottweiler']},
                'sex_upon_outcome': 'Intact Male',
                'age_upon_outcome_in_weeks': {'$gte': 26, '$lte': 156}
            }
        elif filter_type == 'disaster':
            query = {
                'animal_type': 'Dog',
                'breed': {'$in': ['Doberman Pinscher', 'German Shepherd', 'Golden Retriever', 'Bloodhound', 'Rottweiler']},
                'sex_upon_outcome': 'Intact Male',
                'age_upon_outcome_in_weeks': {'$gte': 20, '$lte': 300}
            }
        else:
            query = {}

        # Query the database and update the DataTable
        df = pd.DataFrame.from_records(animals.read(query))
        if '_id' in df.columns:
            df.drop(columns=['_id'], inplace=True)
        return df.to_dict('records')
    except Exception as e:
        return []

# Callback to toggle columns visibility in the DataTable
@app.callback(
    Output('datatable-id', 'hidden_columns'),
    [Input('column-toggle', 'value')]
)
def toggle_columns(selected_columns):
    return [col for col in df.columns if col not in selected_columns] + ALWAYS_HIDDEN

# Callback to update the graphs based on the DataTable data
@app.callback(
    Output('graph-id', "children"),
    [Input('datatable-id', "derived_virtual_data")]
)
def update_graphs(viewData):
    if viewData is None or len(viewData) == 0:
        return [html.Div("No data to display.")]
    df = pd.DataFrame.from_dict(viewData)
    if 'breed' not in df.columns or df.empty:
        return [html.Div("No breed data available.")]
    return [
        dcc.Graph(
            figure=px.pie(df, names='breed', title="Chosen Animals")
        )
    ]
# Highlight selected columns in the DataTable
@app.callback(
    Output('datatable-id', 'style_data_conditional'),
    [Input('datatable-id', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'backgroundColor': '#D2F3FF'
    } for i in selected_columns]

# Callback to update the map based on the selected row in the DataTable
@app.callback(
    Output('map-id', "children"),
    [Input('datatable-id', "derived_virtual_data"),
     Input('datatable-id', "derived_virtual_selected_rows")]
)
def update_map(viewData, index):
    if not viewData:
        return [html.Div("No data to display on the map.")]
    dff = pd.DataFrame.from_dict(viewData)
    if not index or len(index) == 0:
        row = 0
    else:
        row = index[0]
    if 'location_lat' not in dff.columns or 'location_long' not in dff.columns:
        return [html.Div("No location data available.")]
    lat = dff.loc[row, 'location_lat']
    lon = dff.loc[row, 'location_long']
    return [dl.Map(style={'width': '1000px', 'height': '500px'}, center=[lat, lon], zoom=10,
                   children=[
                       dl.TileLayer(id='base-layer-id'),
                       dl.Marker(position=[lat, lon],
                                 children=[
                                     dl.Tooltip(str(dff.loc[row, 'breed'])),
                                     dl.Popup([
                                         html.H1('Animal Name'),
                                         html.P(str(dff.loc[row, 'name']))
                                      ])
                                  ])
                       ])]
# Callback to register a new user
@app.callback(
    Output('register-message', 'children'),
    Input('register-btn', 'n_clicks'),
    State('reg-username', 'value'),
    State('reg-password', 'value')
)
def register_user_callback(n_clicks, username, password):
    if n_clicks and username and password:
        success, msg = animals.register_user(username, password)
        color = 'green' if success else 'red'
        return html.Span(msg, style={'color': color})
    return ""

# Callback to log in a user and manage login state
@app.callback(
    [Output('login-message', 'children'),
     Output('login-state', 'data')],
    Input('login-btn', 'n_clicks'),
    State('login-username', 'value'),
    State('login-password', 'value')
)
def login_user_callback(n_clicks, username, password):
    if n_clicks and username and password:
        success, msg = animals.login_user(username, password)
        color = 'green' if success else 'red'
        login_data = {'logged_in': success, 'username': username if success else None}
        return html.Span(msg, style={'color': color}), login_data
    return "", {'logged_in': False, 'username': None}

# Callback to toggle visibility of protected content based on login state
@app.callback(
    Output('protected-content', 'style'),
    Input('login-state', 'data')
)
def toggle_protected_content(login_data):
    if login_data and login_data.get('logged_in'):
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# Callback to show a login prompt if the user is not logged in
@app.callback(
    Output('login-prompt', 'children'),
    Input('login-state', 'data')
)
def show_login_prompt(login_data):
    if not login_data or not login_data.get('logged_in'):
        return html.Div(
            "Please log in to access the dashboard features.",
            style={'color': 'red', 'fontWeight': 'bold', 'margin': '20px 0'}
        )
    return ""


# Run the app
if __name__ == '__main__':
    app.run(debug=True)

