import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

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

def input_table_size():
    rows = st.number_input("Enter the number of rows:", min_value=1, step=1)
    columns = st.number_input("Enter the number of columns:", min_value=1, step=1)
    return rows, columns

def input_observed_values(rows, columns):
    st.subheader("Enter Observed Values")
    data = []
    for i in range(rows):
        row_data = []
        for j in range(columns):
            value = st.number_input(f"Enter value for row {i+1}, column {j+1}:", min_value=0, step=1)
            row_data.append(value)
        data.append(row_data)
    
    # Convert to DataFrame for displaying in a table
    df = pd.DataFrame(data, columns=[f"Column {i+1}" for i in range(columns)])
    st.dataframe(df, height=150)

    return np.array(data)

def perform_chi_square_test(observed_values):
    # Perform Chi-square test
    st.subheader("Chi-square Test Results")
    chi2, p, _, _ = chi2_contingency(observed_values)
    st.write(f"Chi-square statistic: {chi2}")
    st.write(f"P-value: {p}")

    if p < 0.05:
        st.write("The observed values are significantly different from the expected values.")
    else:
        st.write("No significant difference observed between the observed and expected values.")

    # Display summary statistics
    st.subheader("Summary Statistics")
    summary_table = pd.DataFrame(observed_values, columns=[f"Column {i+1}" for i in range(observed_values.shape[1])])
    st.table(summary_table.describe())

def main():
    create_navbar()

    st.title("Sigma Stats for Chi-square Test")
    st.markdown("---")

    # Input table size
    rows, columns = input_table_size()

    # Input observed values
    observed_values = input_observed_values(rows, columns)

    # Perform Chi-square test on button click
    if st.button("Perform Analysis"):
        perform_chi_square_test(observed_values)

if __name__ == "__main__":
    main()
