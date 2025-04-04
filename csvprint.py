import streamlit as st
import pandas as pd

# URL to the raw CSV file on GitHub
CSV_URL = "https://raw.githubusercontent.com/lab-Kason/GEN/refs/heads/main/food_content.csv"

# Streamlit app
def main():
    st.title("CSV Viewer with Streamlit")

    # Load the CSV file from GitHub
    try:
        data = pd.read_csv(CSV_URL)
        st.write("### CSV Data:")
        st.dataframe(data)  # Display the CSV content in a table
    except Exception as e:
        st.error(f"An error occurred while loading the CSV file: {e}")

if __name__ == "__main__":
    main()