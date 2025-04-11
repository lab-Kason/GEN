import streamlit as st
import pandas as pd

# URL to the raw CSV file on GitHub
CSV_URL = "https://raw.githubusercontent.com/lab-Kason/GEN/main/food_content.csv"

# Set the page layout to wide for better use of screen space
st.set_page_config(page_title="CSV Viewer", layout="wide")

# Streamlit app
def main():
    st.title("CSV Viewer with Streamlit")

    # Load the CSV file from GitHub
    try:
        data = pd.read_csv(CSV_URL)
        st.write("### CSV Data:")
        # Display the CSV content in a table with dynamic width and height
        st.dataframe(data, use_container_width=True, height=600)  # Adjust height for 16:9 ratio
    except Exception as e:
        st.error(f"An error occurred while loading the CSV file: {e}")

if __name__ == "__main__":
    main()
