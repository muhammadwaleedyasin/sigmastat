import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import base64
from dash import dash_table
from io import BytesIO
from scipy.stats import shapiro, skew, kurtosis
import plotly.express as px
from dash.exceptions import PreventUpdate

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Navbar
navbar = dbc.Navbar(
    [
        dbc.NavItem(html.A(html.Img(src='your_logo.png', height='30px', className='float-logo'), href="#")),  # Replace 'your_logo.png' with the path to your logo image
    ],
    color="#47c8ff",  # Change the color to #47c8ff
    dark=True,
    style={'border-bottom': '2px solid black'},  # Add a black border to the bottom
    sticky='top',  # Make the navbar sticky
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
    is_open=False  # Start with the modal closed
)

# Table to display uploaded data
uploaded_data_table = dash_table.DataTable(
    id='uploaded-data-table',
    style_table={'maxHeight': '400px', 'overflowY': 'auto'},
)

# Dropdown for variable selection
variable_dropdown = dcc.Dropdown(
    id='variable-dropdown',
    multi=True,
)

# Button for descriptive statistics
descriptive_stats_btn = dbc.Button('Show Descriptive Statistics', id='descriptive-stats-btn', color='primary', style={'margin-top': '10px', 'margin-bottom': '10px'})

# Result of descriptive statistics
descriptive_stats_result = html.Div(id='descriptive-stats-result')

# Normality test result
normality_test_result = html.Div(id='normality-test-result')

# Box plots for normality check
box_plot_normality = dcc.Graph(id='box-plot-normality')

# Box plots for non-categorical variables
box_plots = html.Div(id='box-plots')

# Side Panel
side_panel = html.Div([
    dbc.Button('Open Upload Modal', id='open-upload-modal-btn', className='btn btn-primary', style={'margin-bottom': '10px', 'margin-top': '10px'}),
    upload_modal,
    html.Br(),
    variable_dropdown,
    descriptive_stats_btn,
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
    descriptive_stats_result,
    html.Hr(),
    html.H4('Normality Check'),
    box_plot_normality,
    normality_test_result,
    html.Hr(),
    html.H4('Box Plots'),
    box_plots,
], style={'padding': '20px', 'margin-left': '25%', 'margin-right': '5%', 'margin-bottom': '80px'})  # Increased margin-bottom to accommodate the footer

# Footer
footer = html.Footer([
    html.A(html.I(className="fab fa-github-square fa-2x"), href="https://github.com", target="_blank", style={'margin-right': '10px'}),
    html.A(html.I(className="fab fa-facebook-square fa-2x"), href="https://facebook.com", target="_blank", style={'margin-right': '10px'}),
    html.A(html.I(className="fab fa-twitter-square fa-2x"), href="https://twitter.com", target="_blank", style={'margin-right': '10px'}),
    html.A(html.I(className="fab fa-instagram-square fa-2x"), href="https://instagram.com", target="_blank", style={'margin-right': '10px'}),
    html.A("yourwebsite.com", href="https://yourwebsite.com", target="_blank"),
], style={'text-align': 'center', 'padding': '5px', 'position': 'fixed', 'bottom': '0', 'width': '100%', 'background-color': '#f8f9fa'})

# App Layout
app.layout = html.Div([
    navbar,
    side_panel,
    center_content,
    footer,
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

# Callback to show descriptive statistics and perform normality test
@app.callback(
    [Output('descriptive-stats-result', 'children'),
     Output('normality-test-result', 'children'),
     Output('box-plot-normality', 'figure'),
     Output('box-plots', 'children')],  # Change 'figure' to 'children' for box plots
    [Input('descriptive-stats-btn', 'n_clicks')],
    [State('variable-dropdown', 'value'),
     State('uploaded-data-table', 'data')]
)
def show_descriptive_stats(n_clicks, selected_variables, uploaded_data):
    if not n_clicks or not selected_variables:
        raise PreventUpdate

    df = pd.DataFrame(uploaded_data)

    descriptive_stats_result = []
    normality_test_results = []
    box_plot_figures = []
    box_plots_html = []

    for variable in selected_variables:
        try:
            # Descriptive statistics
            mean = df[variable].mean()
            median = df[variable].median()
            mode = df[variable].mode().values.tolist()
            skewness_val = skew(df[variable])
            kurtosis_val = kurtosis(df[variable])
            std_dev = df[variable].std()
            quartiles = df[variable].quantile([0.25, 0.5, 0.75]).tolist()

            # Format descriptive statistics as a single string with line breaks and bold headings
            descriptive_stats_text = (
                f"**Descriptive Statistics of {variable}:**\n"
                f"Mean = {mean:.4f}\n"
                f"Median = {median:.4f}\n"
                f"Mode = {mode}\n"
                f"Skewness = {skewness_val:.4f}\n"
                f"Kurtosis = {kurtosis_val:.4f}\n"
                f"Standard Deviation = {std_dev:.4f}\n"
                f"Quartiles = {quartiles}\n"
            )

            descriptive_stats_result.append(html.P(descriptive_stats_text, style={'white-space': 'pre-line'}))

            # Perform Shapiro-Wilk test for normality
            stat, p_value = shapiro(df[variable])
 
            # Display normality test result
            if p_value > 0.05:
                normality_test_results.append(f"The variable {variable} appears to be normally distributed (p-value = {p_value:.4f})")
            else:
                normality_test_results.append(f"The variable {variable} does not appear to be normally distributed (p-value = {p_value:.4f})")

            # Create box plot for normality check
            box_plot_figures.append(px.box(df, x=variable, title=f'Box Plot for {variable}'))

            # Create box plot for non-categorical variables
            if df[variable].dtype != 'object':
                box_plots_html.append(dcc.Graph(figure=px.box(df, x=df.index, y=df[variable], title=f'Box Plot for {variable}')))
            else:
                box_plots_html.append(None)

        except Exception as e:
            descriptive_stats_result.append(html.P(f"Descriptive Statistics for {variable}: None, Wrong data selected. Error: {str(e)}", style={'white-space': 'pre-line'}))
            normality_test_results.append(f"The variable {variable}: None, Wrong data selected. Error: {str(e)}")
            box_plot_figures.append(None)
            box_plots_html.append(None)

    # Combine box plots into a single figure
    combined_box_plot = px.box(df, x=selected_variables, title='Combined Box Plots for Normality Check')

    return descriptive_stats_result, html.Div(normality_test_results), combined_box_plot, box_plots_html

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

