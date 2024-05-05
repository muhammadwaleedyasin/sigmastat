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
            <a href="https://sigmastat.org/">Home</a>
            <a href="https://sigmastat.org/about/about-us.html">About</a>
            <a href="https://sigmastat.org/contact.html">Contact</a>
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
    selected_vars = st.sidebar.multiselect("Select Variables for Correlation Analysis", df.columns)
    return selected_vars

def generate_report(df, selected_vars):
    # Display box Plot with heading "Normality Testing"
    st.subheader("Normality Testing")
    fig = px.box(df, x=selected_vars, title="")
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

    # Display scatter plot and correlation coefficient using Plotly
    if len(selected_vars) == 2:
        st.subheader("Correlation Analysis")
        correlation_plot = px.scatter(df, x=selected_vars[0], y=selected_vars[1], title="")
        correlation_plot.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True, title_text=selected_vars[0], zeroline=False)
        correlation_plot.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True, title_text=selected_vars[1], zeroline=False)
        st.plotly_chart(correlation_plot)

        correlation_coefficient = df[selected_vars[0]].corr(df[selected_vars[1]])
        st.write(f"Correlation Coefficient: {correlation_coefficient}")
        return correlation_coefficient
    else:
        st.warning("Please select exactly 2 variables for correlation analysis.")
        return None

def perform_correlation_analysis(df, selected_vars, analysis_performed):
    if st.button("Perform Correlation Analysis") and not analysis_performed:
        correlation_coefficient = generate_report(df, selected_vars)
        return True, correlation_coefficient
    return analysis_performed, None

def main():
    create_navbar()

    st.title("Sigma Stats for Correlation Analysis")
    st.markdown("---")

    uploaded_file = upload_csv_file()

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        display_spreadsheet(df)

        selected_vars = select_variables(df)

        # Track if correlation analysis has been performed
        analysis_performed = st.session_state.get('analysis_performed', False)

        if selected_vars and len(selected_vars) == 2:
            analysis_performed, correlation_coefficient = perform_correlation_analysis(df, selected_vars, analysis_performed)

            if analysis_performed:
                st.success("Correlation Analysis has been performed!")

        elif selected_vars and len(selected_vars) != 2:
            st.warning("Please select exactly 2 variables for correlation analysis.")

        # Save the state of analysis_performed
        st.session_state.analysis_performed = analysis_performed

if __name__ == "__main__":
    main()
