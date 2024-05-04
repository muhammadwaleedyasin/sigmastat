import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from scipy.stats import chi2_contingency
import pandas as pd
import numpy as np

# Initialize the Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Define the layout of the app
app.layout = dbc.Container([
    # Sticky Navbar
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="#")),
        ],
        brand="Chi-Square Test App",
        brand_href="#",
        color="primary",
        dark=True,
        sticky="top",
    ),
    dbc.Row([
        dbc.Col([
            # Left Side Panel
            html.Div([
                dbc.Label("Number of Rows:"),
                dbc.Input(id="num-rows", type="number", min=1, value=2),
                dbc.Label("Number of Columns:"),
                dbc.Input(id="num-cols", type="number", min=1, value=2),
                dbc.Button("Create Table", id="create-table-btn", color="primary", className="mr-2", style={'marginTop': '10px'}),
                dbc.Button("Perform Chi-square Test", id="chi-square-btn", color="success", className="mr-2", style={'marginTop': '10px'}),
            ], style={'marginTop': 20}),
        ], width=3),
        dbc.Col([
            # Center Table and Chi-Square Test Result
            html.Div(id="table-container", style={'marginTop': '20px'}),
            html.Div(id="result-output", style={'marginTop': '20px'}),
        ], width=9),
    ]),
], fluid=True)

# Callback to generate the table based on rows and columns input
@app.callback(
    Output("table-container", "children"),
    Input("create-table-btn", "n_clicks"),
    [State("num-rows", "value"), State("num-cols", "value")],
)
def create_table(n_clicks, rows, cols):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    
    columns = [{'name': f'Column {i+1}', 'id': f'column-{i}'} for i in range(cols)]
    data = [{f'column-{i}': '' for i in range(cols)} for _ in range(rows)]
    
    return dash_table.DataTable(
        id='input-table',
        columns=columns,
        data=data,
        editable=True,
        row_deletable=True,
        style_table={'overflowX': 'auto'},  # Makes table horizontally scrollable
    )

# Callback to perform the Chi-square test
@app.callback(
    Output("result-output", "children"),
    Input("chi-square-btn", "n_clicks"),
    State("input-table", "data"),
    prevent_initial_call=True
)
def perform_chi_square(n_clicks, table_data):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate

    df = pd.DataFrame(table_data)
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    chi2, p, dof, expected = chi2_contingency(df)
    
    return [
        html.H5("Chi-square Test Result:"),
        html.P(f"Chi-square statistic: {chi2:.4f}"),
        html.P(f"P-value: {p:.4f}"),
        html.P(f"Degrees of freedom: {dof}"),
        html.P("Expected frequencies:"),
        html.Pre(np.array_str(expected, precision=3)),
    ]

if __name__ == "__main__":
    app.run_server(debug=True)
