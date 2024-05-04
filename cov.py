import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import base64
import numpy as np
import plotly.express as px
from scipy.stats import pearsonr, shapiro
from dash import dash_table
from io import BytesIO
import matplotlib.pyplot as plt
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
    multi=True,
)

# Button for covariance analysis
covariance_btn = dbc.Button('Perform Covariance Analysis', id='covariance-btn', color='primary', style={'margin-top': '10px', 'margin-bottom': '10px'})

# Result of covariance analysis
covariance_result = html.Div(id='covariance-result')

# Invert axis button
invert_axis_btn = dbc.Button('Invert Axis', id='invert-axis-btn', color='info', className='ml-2', style={'margin-bottom': '10px'})

# Graph for covariance
covariance_graph = dcc.Graph(id='covariance-graph')

# Box plots for normality check
box_plot_normality = dcc.Graph(id='box-plot-normality')

# Normality test result
normality_test_result = html.Div(id='normality-test-result')

# Side Panel
side_panel = html.Div([
    dbc.Button('Open Upload Modal', id='open-upload-modal-btn', className='btn btn-primary', style={'margin-bottom': '10px', 'margin-top': '10px'}),
    upload_modal,
    html.Br(),
    variable_dropdown,
    covariance_btn,
    invert_axis_btn,
], style={'padding': '20px', 'width': '20%', 'position': 'fixed', 'left': '0', 'background-color': '#dcdcdc', 'border-right': '2px solid lightgrey', 'height': '100vh'})

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
    covariance_result,
    covariance_graph,
    html.Br(),
    html.Hr(),
    html.H4('Normality Check'),
    box_plot_normality,
    normality_test_result,
], style={'padding': '20px', 'margin-left': '25%', 'margin-right': '5%'})

# Footer
footer = html.Footer([
    html.A(html.I(className="fab fa-github-square fa-2x"), href="https://github.com", target="_blank", style={'margin-right': '10px'}),
    html.A(html.I(className="fab fa-facebook-square fa-2x"), href="https://facebook.com", target="_blank", style={'margin-right': '10px'}),
    html.A(html.I(className="fab fa-twitter-square fa-2x"), href="https://twitter.com", target="_blank", style={'margin-right': '10px'}),
    html.A(html.I(className="fab fa-instagram-square fa-2x"), href="https://instagram.com", target="_blank", style={'margin-right': '10px'}),
    html.A("sigmastats.org", href="https://yourwebsite.com", target="_blank"),
], style={'text-align': 'center', 'padding': '5px', 'position': 'fixed', 'bottom': '0', 'width': '100%', 'background-color': '#f8f9fa'})

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
        # Return an empty structure if no content
        empty_columns = [{'name': f'Column {i}', 'id': f'Column {i}'} for i in range(1, 6)]
        empty_data = [{'Column 1': None, 'Column 2': None, 'Column 3': None, 'Column 4': None, 'Column 5': None} for _ in range(10)]
        return empty_data, empty_columns

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(BytesIO(decoded))

    # Display all rows of the uploaded data
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
        # Return empty options if no columns
        return []

    return [{'label': col['name'], 'value': col['id']} for col in columns]

# Callback to perform covariance analysis, display the result, and handle axis inversion
@app.callback(
    [Output('covariance-graph', 'figure'),
     Output('covariance-result', 'children')],
    [Input('covariance-btn', 'n_clicks'),
     Input('invert-axis-btn', 'n_clicks')],
    [State('variable-dropdown', 'value'),
     State('uploaded-data-table', 'data'),
     State('covariance-graph', 'figure')]
)
def update_covariance_graph(covariance_clicks, invert_clicks, selected_variables, uploaded_data, current_figure):
    # Check which button triggered the callback
    ctx = dash.callback_context
    button_id = ctx.triggered_id

    if not button_id:
        raise PreventUpdate

    # Convert uploaded_data to DataFrame
    df = pd.DataFrame(uploaded_data)

    # Default output (no update)
    figure = {}
    result_text = dash.no_update

    # Covariance analysis button clicked
    if button_id == 'covariance-btn' and selected_variables and len(selected_variables) == 2:
        # Filter out NaN and infinite values
        df_filtered = df[selected_variables].replace([np.inf, -np.inf], np.nan).dropna()

        # Perform covariance analysis
        if not df_filtered.empty:
            covariance_matrix = np.cov(df_filtered[selected_variables], rowvar=False)

            # Update the covariance graph figure
            fig, ax = plt.subplots()
            ax.scatter(df_filtered[selected_variables[0]], df_filtered[selected_variables[1]])
            ax.set_title(f'Covariance between {selected_variables[0]} and {selected_variables[1]}')
            ax.set_xlabel(selected_variables[0])
            ax.set_ylabel(selected_variables[1])

            # Convert Matplotlib figure to Dash-compatible format
            figure = {
                'data': [{'x': df_filtered[selected_variables[0]], 'y': df_filtered[selected_variables[1]], 'type': 'scatter', 'mode': 'markers'}],
                'layout': {'title': f'Covariance between {selected_variables[0]} and {selected_variables[1]}',
                           'xaxis': {'title': selected_variables[0]},
                           'yaxis': {'title': selected_variables[1]}}
            }

            result_text = f"The Covariance between {selected_variables[0]} and {selected_variables[1]} is: {covariance_matrix[0, 1]:.4f}"

    # Invert axis button clicked
    elif button_id == 'invert-axis-btn' and current_figure is not None:
        # Invert the axis labels and values
        current_layout = current_figure.get('layout', {})
        new_layout = {'xaxis': current_layout.get('yaxis', {}),
                      'yaxis': current_layout.get('xaxis', {})}
        current_figure['layout'] = new_layout

        # Invert the rows of the uploaded data
        df[selected_variables[0]], df[selected_variables[1]] = df[selected_variables[1]], df[selected_variables[0]].copy()

        # Invert the values in the covariance graph figure
        if 'data' in current_figure:
            for trace in current_figure['data']:
                trace['x'], trace['y'] = trace['y'], trace['x']

        figure = current_figure

    return figure, result_text

# Callback to check normality and display box plots
@app.callback(
    [Output('box-plot-normality', 'figure'),
     Output('normality-test-result', 'children')],
    [Input('variable-dropdown', 'value'),
     Input('uploaded-data-table', 'data')]
)
def check_normality(selected_variables, uploaded_data):
    if not selected_variables:
        raise PreventUpdate

    df = pd.DataFrame(uploaded_data)

    box_plot_figures = []
    normality_test_results = []

    for variable in selected_variables:
        # Create box plot
        box_plot_figures.append(px.box(df, x=variable, title=f'Box Plot for {variable}'))

        # Perform Shapiro-Wilk test for normality
        stat, p_value = shapiro(df[variable])

        # Display result
        if p_value > 0.05:
            normality_test_results.append(f"The variable {variable} appears to be normally distributed (p-value = {p_value:.4f})")
        else:
            normality_test_results.append(f"The variable {variable} does not appear to be normally distributed (p-value = {p_value:.4f})")

    # Combine box plots into a single figure
    combined_box_plot = px.box(df, x=selected_variables, title='Combined Box Plots for Normality Check')

    return combined_box_plot, html.Div(normality_test_results)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
