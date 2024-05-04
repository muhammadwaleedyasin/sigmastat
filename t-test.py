import streamlit as st
import pandas as pd
from scipy.stats import ttest_1samp, shapiro
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

def select_variable(df):
    selected_var = st.sidebar.selectbox("Select a Variable for One-Sample t-test", df.columns)
    return selected_var

def perform_one_sample_t_test(df, selected_var, mu, test_performed):
    if st.button("Perform One-Sample t-test") and not test_performed:
        if selected_var:
            # Display normality testing before t-test
            st.subheader("Normality Testing")

            # Shapiro-Wilk test for normality
            _, p_value = shapiro(df[selected_var])
            st.write(f"Shapiro-Wilk p-value for {selected_var}: {p_value}")

            # Interpret normality test results
            if p_value > 0.05:
                st.write(f"{selected_var} appears to be normally distributed.")
            else:
                st.write(f"{selected_var} does not appear to be normally distributed.")

            # Box plot for normality visualization
            fig = px.box(df, x=selected_var, points="all", labels={selected_var: f"{selected_var} Boxplot"})
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

            # Perform one-sample t-test
            result = ttest_1samp(df[selected_var], mu)
            
            # Display t-test results
            st.subheader("One-Sample t-test Results")
            st.write(f"T-statistic: {result.statistic}")
            st.write(f"P-value: {result.pvalue}")

            if result.pvalue < 0.05:
                st.write(f"The mean of {selected_var} is significantly different from the specified population mean (mu).")
            else:
                st.write(f"No significant difference observed between the mean of {selected_var} and the specified population mean (mu).")

            # Display statistical summary table
            st.subheader("Statistical Summary Table")
            summary_table = df[selected_var].describe().transpose()
            st.table(summary_table)

            return True
        else:
            st.warning("Please select a variable for one-sample t-test.")
            return False
    return test_performed

def main():
    create_navbar()

    st.title("Sigma Stats for One-Sample t-test")
    st.markdown("---")

    uploaded_file = upload_csv_file()

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        display_spreadsheet(df)

        selected_var = select_variable(df)

        # Track if one-sample t-test has been performed
        test_performed = st.session_state.get('test_performed', False)

        if selected_var:
            # Specify the population mean (mu)
            mu = st.sidebar.number_input("Enter the Population Mean (mu)", value=0.0)

            test_performed = perform_one_sample_t_test(df, selected_var, mu, test_performed)

            if test_performed:
                st.success("One-Sample t-test has been performed!")

        # Save the state of test_performed
        st.session_state.test_performed = test_performed

if __name__ == "__main__":
    main()
