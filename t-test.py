import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import base64
import numpy as np
import plotly.express as px
from dash import dash_table
from io import BytesIO
from scipy.stats import ttest_1samp, shapiro
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from dash.exceptions import PreventUpdate
import os

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Set the Matplotlib backend to a non-GUI one
plt.switch_backend('agg')

# Navbar
navbar = dbc.Navbar(
    [
        dbc.NavItem(html.A(html.Img(src='Data Analysis.png', height='30px', className='float-logo'), href="#")),
        dbc.NavItem(dbc.NavLink("GitHub", href="https://sigmastas.org", external_link=True)),
    ],
    color="#47c8ff",
    dark=True,
    style={'border-bottom': '2px solid black'},
    sticky='top',
)

# Modal for file upload
upload_modal = dbc.Modal(
    [
        dbc.ModalHeader("Upload CSV File"),
        dbc.ModalBody([
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                multiple=False
            ),
        ]),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-upload-modal", className="ml-auto")
        ),
    ],
    id="upload-modal",
    is_open=False
)

# Table to display uploaded data
uploaded_data_table = dash_table.DataTable(
    id='uploaded-data-table',
    style_table={'maxHeight': '400px', 'overflowY': 'auto'},
    editable=True,
)

# Dropdown for variable selection
variable_dropdown = dcc.Dropdown(
    id='variable-dropdown',
    multi=False,
)

# Input for t-test mu value
ttest_mu_input = dcc.Input(
    id='ttest-mu-input',
    type='number',
    placeholder='Enter mu value',
)

# Button for one-sample t-test
ttest_btn = dbc.Button('Perform One-Sample T-Test', id='ttest-btn', color='primary', style={'margin-top': '10px', 'margin-bottom': '10px'})

# Result of one-sample t-test
ttest_result = html.Div(id='ttest-result')

# Normality test graph
normality_test_graph = dcc.Graph(id='normality-test-graph')

# Normality test result
normality_test_result = html.Div(id='normality-test-result')

# Summary statistics
summary_statistics = html.Div(id='summary-statistics')

# Side Panel
side_panel = html.Div([
    dbc.Button('Open Upload Modal', id='open-upload-modal-btn', className='btn btn-primary', style={'margin-bottom': '10px', 'margin-top': '10px'}),
    upload_modal,
    html.Br(),
    variable_dropdown,
    ttest_mu_input,
    ttest_btn,
], style={'padding': '20px', 'width': '20%', 'position': 'fixed', 'left': '0', 'background-color': '#dcdcdc',
          'border-right': '2px solid lightgrey', 'height': '100vh'})

# Center Content
center_content = html.Div([
    dcc.Loading(
        id='loading-upload',
        type='circle',
        children=[
            uploaded_data_table,
        ]
    ),
    html.Br(),
    normality_test_graph,
    normality_test_result,
    html.Br(),
    summary_statistics,
    ttest_result,
], style={'padding': '20px', 'margin-left': '25%', 'margin-right': '5%'})

# Footer
footer = html.Footer([
    html.A(html.I(className="fab fa-github-square fa-2x"), href="https://github.com", target="_blank", style={'margin-right': '10px'}),
    html.A(html.I(className="fab fa-facebook-square fa-2x"), href="https://facebook.com", target="_blank", style={'margin-right': '10px'}),
    html.A(html.I(className="fab fa-twitter-square fa-2x"), href="https://twitter.com", target="_blank", style={'margin-right': '10px'}),
    html.A(html.I(className="fab fa-instagram-square fa-2x"), href="https://instagram.com", target="_blank", style={'margin-right': '10px'}),
    html.A("sigmastats.org", href="https://yourwebsite.com", target="_blank"),
], style={'text-align': 'center', 'padding': '5px', 'position': 'fixed', 'bottom': '0', 'width': '100%',
          'background-color': '#f8f9fa'})

# App Layout
app.layout = html.Div([
    navbar,
    side_panel,
    center_content,
    footer,
    dbc.Button('Reload the App', id='reload', color='primary', style={'float': 'right'}),
])

# Callback to open and close the upload modal
@app.callback(
    Output("upload-modal", "is_open"),
    [Input("open-upload-modal-btn", "n_clicks"), Input("close-upload-modal", "n_clicks")],
    [State("upload-modal", "is_open")],
)
def toggle_upload_modal(open_btn_clicks, close_btn_clicks, is_open):
    ctx = dash.callback_context

    if not ctx.triggered_id:
        raise PreventUpdate

    button_id = ctx.triggered_id.split('.')[0]

    if button_id == "open-upload-modal-btn" and open_btn_clicks:
        return True
    elif button_id == "close-upload-modal" and close_btn_clicks:
        return False

    return is_open

# Callback to display the uploaded data in the table
@app.callback(
    Output('uploaded-data-table', 'data'),
    Output('uploaded-data-table', 'columns'),
    [Input('upload-data', 'contents')]
)
def update_uploaded_data(contents):
    if contents is None:
        empty_columns = [{'name': f'Column {i}', 'id': f'Column {i}'} for i in range(1, 6)]
        empty_data = [{'Column 1': None, 'Column 2': None, 'Column 3': None, 'Column 4': None, 'Column 5': None} for _ in range(10)]
        return empty_data, empty_columns

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(BytesIO(decoded))

    columns = [{'name': col, 'id': col} for col in df.columns]
    data = df.to_dict('records')

    return data, columns

# Callback to update variable dropdown options
@app.callback(
    Output('variable-dropdown', 'options'),
    [Input('uploaded-data-table', 'columns')]
)
def update_variable_dropdown(columns):
    if not columns:
        return []

    return [{'label': col['name'], 'value': col['id']} for col in columns]

# Callback to perform one-sample t-test, display the result, and handle normality test
@app.callback(
    [Output('normality-test-graph', 'figure'),
     Output('normality-test-result', 'children'),
     Output('summary-statistics', 'children'),
     Output('ttest-result', 'children')],
    [Input('ttest-btn', 'n_clicks')],
    [State('variable-dropdown', 'value'),
     State('ttest-mu-input', 'value'),
     State('uploaded-data-table', 'data')]
)
def perform_ttest(ttest_clicks, selected_variable, ttest_mu, uploaded_data):
    ctx = dash.callback_context

    if not ctx.triggered_id or not ttest_clicks or not selected_variable or ttest_mu is None:
        raise PreventUpdate

    # Convert uploaded_data to DataFrame
    df = pd.DataFrame(uploaded_data)

    # Filter out NaN and infinite values for selected variable
    df_filtered = df[selected_variable].replace([np.inf, -np.inf], np.nan).dropna()

    # Perform Shapiro-Wilk test for normality
    stat, p_value = shapiro(df_filtered)

    # Plot normality test results using a box plot
    fig_normality = px.box(df, y=selected_variable, title=f'Normality Test for {selected_variable}')

    # Display normality test result with formatted p-value
    normality_result = f"Shapiro-Wilk Test for Normality (p-value): {p_value:.5f}"
    if p_value > 0.05:
        normality_result += f"\nThe variable {selected_variable} appears to be normally distributed."
    else:
        normality_result += f"\nThe variable {selected_variable} does not appear to be normally distributed."

    # Display summary statistics
    summary_stats = df_filtered.describe().to_frame().reset_index().rename(columns={'index': 'Statistics', selected_variable: 'Value'})
    summary_stats_table = dash_table.DataTable(
        id='summary-stats-table',
        columns=[{'name': col, 'id': col} for col in summary_stats.columns],
        data=summary_stats.to_dict('records'),
        style_table={'maxHeight': '200px', 'overflowY': 'auto'},
    )

    # Perform one-sample t-test
    t_stat, p_value_ttest = ttest_1samp(df_filtered, ttest_mu)

    # Display t-test result with formatted p-value
    ttest_result_text = f"One-Sample T-Test for {selected_variable} with μ={ttest_mu}:"
    ttest_result_text += f"\n\nT-statistic: {t_stat:.4f}\nP-value: {p_value_ttest:.5f}"

    return fig_normality, normality_result, summary_stats_table, ttest_result_text

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
