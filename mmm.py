import streamlit as st
import pandas as pd
from scipy.stats import shapiro
import plotly.express as px

def create_navbar():
    st.markdown(
        """
        <style>
        body {
            margin: 0;
        }

        .navbar {
            background-color: #317EFB;
            padding: 10px;
            width: 100%;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .navbar a {
            color: white;
            text-decoration: none;
            margin: 0 15px;
        }

        .navbar a:hover {
            text-decoration: underline;
        }
        </style>
        
        <div class="navbar">
            <a href="http://127.0.0.1:5501/index.html">Home</a>
            <a href="#">About</a>
            <a href="#">Contact</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

def upload_csv_file():
    return st.sidebar.file_uploader("Upload CSV File", type=["csv"])

def display_spreadsheet(df):
    st.dataframe(df, height=300)
    st.write("")  # Add an empty line to separate plots

def select_variables(df):
    selected_vars = st.sidebar.multiselect("Select Variables for Analysis", df.columns)
    return selected_vars

def generate_report(df, selected_vars):
    # Display box Plot with heading "Normality Testing"
    st.subheader("Normality Testing")
    fig = px.box(df[selected_vars], title="")
    fig.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, b=10, t=10),
        boxmode='overlay',
        boxgap=0.5,
        boxgroupgap=0.3,
        height=400,  # Adjust the height as needed
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
    st.plotly_chart(fig)
    st.write("")  # Add an empty line to separate plots

    # Performing normality checks and displaying results
    for var in selected_vars:
        st.subheader(f"Variable: {var}")

        # Perform Shapiro-Wilk test for normality
        _, p_value = shapiro(df[var])
        st.write(f"Shapiro-Wilk p-value for {var}: {p_value}")

        # Interpret normality test results
        if p_value > 0.05:
            st.write(f"{var} appears to be normally distributed.")
        else:
            st.write(f"{var} does not appear to be normally distributed.")

    # Display mean, median, and mode for selected variables
    st.subheader("Descriptive Statistics")
    for var in selected_vars:
        st.write(f"{var}:")
        st.write(f"Mean: {df[var].mean()}")
        st.write(f"Median: {df[var].median()}")
        st.write(f"Mode: {df[var].mode().iloc[0]}")
        st.write("")  # Add an empty line between variables

def perform_analysis(df, selected_vars, analysis_performed):
    if st.button("Perform Analysis") and not analysis_performed:
        generate_report(df, selected_vars)
        return True
    return analysis_performed

def main():
    create_navbar()

    st.title("Sigma Stats for Mean, Median, and Mode Analysis")
    st.markdown("---")

    uploaded_file = upload_csv_file()

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        display_spreadsheet(df)

        selected_vars = select_variables(df)

        # Track if analysis has been performed
        analysis_performed = st.session_state.get('analysis_performed', False)

        if selected_vars:
            analysis_performed = perform_analysis(df, selected_vars, analysis_performed)

            if analysis_performed:
                st.success("Analysis has been performed!")

        # Save the state of analysis_performed
        st.session_state.analysis_performed = analysis_performed

if __name__ == "__main__":
    main()
