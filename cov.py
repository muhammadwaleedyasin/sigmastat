import streamlit as st
import pandas as pd
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
    selected_vars = st.sidebar.multiselect("Select Variables for Covariance Analysis", df.columns)
    return selected_vars

def generate_report(df, selected_vars):
    # Display covariance matrix
    st.subheader("Covariance Matrix")
    covariance_matrix = df[selected_vars].cov()
    st.dataframe(covariance_matrix)

    # Display scatter plot matrix
    st.subheader("Scatter Plot Matrix")
    scatter_matrix = px.scatter_matrix(df[selected_vars])
    st.plotly_chart(scatter_matrix)

def perform_covariance_analysis(df, selected_vars, analysis_performed):
    if st.button("Perform Covariance Analysis") and not analysis_performed:
        generate_report(df, selected_vars)
        return True
    return analysis_performed

def main():
    create_navbar()

    st.title("Sigma Stats for Covariance Analysis")
    st.markdown("---")

    uploaded_file = upload_csv_file()

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        display_spreadsheet(df)

        selected_vars = select_variables(df)

        # Track if covariance analysis has been performed
        analysis_performed = st.session_state.get('analysis_performed', False)

        if selected_vars and len(selected_vars) > 1:
            analysis_performed = perform_covariance_analysis(df, selected_vars, analysis_performed)

            if analysis_performed:
                st.success("Covariance Analysis has been performed!")

        elif selected_vars and len(selected_vars) <= 1:
            st.warning("Please select more than 1 variable for covariance analysis.")

        # Save the state of analysis_performed
        st.session_state.analysis_performed = analysis_performed

if __name__ == "__main__":
    main()
