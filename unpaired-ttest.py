import streamlit as st
import pandas as pd
from scipy.stats import ttest_ind, shapiro
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
    selected_vars = st.sidebar.multiselect("Select Two Variables for Unpaired t-test", df.columns)
    return selected_vars

def perform_unpaired_t_test(df, selected_vars, test_performed):
    if st.button("Perform Unpaired t-test") and not test_performed:
        if len(selected_vars) == 2:
            # Display normality testing before t-test
            st.subheader("Normality Testing")

            # Box plot for normality visualization
            fig = px.box(df, x=selected_vars, points="all", labels={var: f"{var} Boxplot" for var in selected_vars})
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

            for var in selected_vars:
                st.subheader(f"Variable: {var}")

                # Shapiro-Wilk test for normality
                _, p_value = shapiro(df[var])
                st.write(f"Shapiro-Wilk p-value for {var}: {p_value}")

                # Interpret normality test results
                if p_value > 0.05:
                    st.write(f"{var} appears to be normally distributed.")
                else:
                    st.write(f"{var} does not appear to be normally distributed.")

            # Perform unpaired t-test
            result = ttest_ind(df[selected_vars[0]], df[selected_vars[1]], equal_var=False)
            
            # Display t-test results
            st.subheader("Unpaired t-test Results")
            st.write(f"T-statistic: {result.statistic}")
            st.write(f"P-value: {result.pvalue}")

            if result.pvalue < 0.05:
                st.write("The means of the two selected variables are significantly different.")
            else:
                st.write("No significant difference observed between the means of the two selected variables.")

            # Display statistical summary table
            st.subheader("Statistical Summary Table")
            summary_table = df[selected_vars].describe().transpose()
            st.table(summary_table)

            return True
        else:
            st.warning("Please select exactly 2 variables for unpaired t-test.")
            return False
    return test_performed

def main():
    create_navbar()

    st.title("Sigma Stats for Unpaired t-test")
    st.markdown("---")

    uploaded_file = upload_csv_file()

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        display_spreadsheet(df)

        selected_vars = select_variables(df)

        # Track if unpaired t-test has been performed
        test_performed = st.session_state.get('test_performed', False)

        if selected_vars:
            test_performed = perform_unpaired_t_test(df, selected_vars, test_performed)

            if test_performed:
                st.success("Unpaired t-test has been performed!")

        # Save the state of test_performed
        st.session_state.test_performed = test_performed

if __name__ == "__main__":
    main()
