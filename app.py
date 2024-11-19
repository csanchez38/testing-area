import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title of the app
st.title("California 2019 Air Quality Visualization App")

# File name (assumed to be in the same directory as the script)
file_name = "California2019.xlsx"

try:
    # Read the Excel file and list available sheets
    excel_data = pd.ExcelFile(file_name)
    sheet_names = excel_data.sheet_names

    # Dropdown to select the sheet
    selected_sheet = st.selectbox("Select a sheet to analyze", sheet_names)

    # Read the selected sheet into a DataFrame
    data = pd.read_excel(file_name, sheet_name=selected_sheet)

    # Drop rows where 'Date' or 'Daily Mean' are missing
    data = data.dropna(subset=['Date', 'Daily Mean'])

    # Convert 'Date' column to datetime format for proper handling
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
    data = data.dropna(subset=['Date'])  # Drop rows where Date conversion fails

    st.write(f"### Data Preview from {selected_sheet} sheet (Filtered)")
    st.dataframe(data.head())

    # Dropdowns for selecting columns
    x_column = st.selectbox("Select X-axis column", ['Date'])
    y_column = st.selectbox("Select Y-axis column", ['Daily Mean', 'Daily AQI Value'])

    # Dropdown for graph type
    graph_type = st.selectbox(
        "Select Graph Type",
        ["Line", "Scatter", "Bar"]
    )

    # Plot button
    if st.button("Plot Graph"):
        fig, ax = plt.subplots()

        if graph_type == "Line":
            ax.plot(data[x_column], data[y_column], marker='o')
            ax.set_title(f"{y_column} vs {x_column} (Line Plot)")

        elif graph_type == "Scatter":
            ax.scatter(data[x_column], data[y_column])
            ax.set_title(f"{y_column} vs {x_column} (Scatter Plot)")

        elif graph_type == "Bar":
            ax.bar(data[x_column], data[y_column])
            ax.set_title(f"{y_column} vs {x_column} (Bar Chart)")

        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column)
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
        st.pyplot(fig)

    st.write("Tip: Ensure the selected columns are numeric for meaningful plots.")
except FileNotFoundError:
    st.error("The file 'California2019.xlsx' was not found. Ensure it is included in the repository.")
