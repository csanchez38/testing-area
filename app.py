import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Define the file name (assuming it is in the same directory as your script)
file_name = "California2019.xlsx"

# Title of the app
st.title("California 2019 Air Quality Visualization App")

try:
    # Read the Excel file and list available sheets
    excel_data = pd.ExcelFile(file_name)
    sheet_names = excel_data.sheet_names

    # Dropdown to select the sheet
    selected_sheet = st.selectbox("Select a sheet to analyze", sheet_names)

    # Read the selected sheet into a DataFrame
    data = pd.read_excel(file_name, sheet_name=selected_sheet, header=0)

    # Rename columns dynamically based on their position
    column_mapping = {
        data.columns[0]: 'Date',
        data.columns[1]: 'Measurement',
        data.columns[2]: 'Units',
        data.columns[3]: 'Daily AQI Value'
    }
    data.rename(columns=column_mapping, inplace=True)

    # Convert 'Date' column to datetime format
    data['Date'] = pd.to_datetime(data['Date'], format='%m/%d/%Y', errors='coerce')
    data = data.dropna(subset=['Date'])  # Drop rows where 'Date' conversion failed

    # Sort the data by Date
    data = data.sort_values(by='Date')

    # Ensure numeric columns are clean
    data['Measurement'] = pd.to_numeric(data['Measurement'], errors='coerce')
    if 'Daily AQI Value' in data.columns:
        data['Daily AQI Value'] = pd.to_numeric(data['Daily AQI Value'], errors='coerce')

    # Drop rows where 'Measurement' is missing
    data = data.dropna(subset=['Measurement'])

    # Extract the unit of measurement dynamically
    unit_of_measurement = data['Units'].iloc[0] if 'Units' in data.columns and not data['Units'].isnull().all() else "Unknown Units"

    # Inform the user if the AQI column is missing or empty
    if data['Daily AQI Value'].isnull().all():
        st.warning("The 'Daily AQI Value' column is empty or unavailable for this dataset. Only the 'Measurement' column is available for plotting.")
        available_y_columns = ['Measurement']
    else:
        available_y_columns = ['Measurement', 'Daily AQI Value']

    # Display a preview of the filtered and sorted data
    st.write("Filtered and Sorted Data Preview:")
    st.dataframe(data.head())

    # Dropdowns for selecting columns
    x_column = st.selectbox("Select X-axis column", ['Date'])
    y_column = st.selectbox("Select Y-axis column", available_y_columns)

    # Dropdown for data aggregation
    aggregation = st.selectbox(
        "Simplify data by:",
        ["None (Daily Data)", "Weekly", "Monthly"]
    )

    # Aggregate data based on the selected aggregation level
    if aggregation == "Weekly":
        # Resample only numeric columns and reset the index
        numeric_data = data.set_index('Date')[['Measurement'] + (['Daily AQI Value'] if 'Daily AQI Value' in data.columns else [])].resample('W').mean().reset_index()
        data = numeric_data
    elif aggregation == "Monthly":
        # Resample only numeric columns and reset the index
        numeric_data = data.set_index('Date')[['Measurement'] + (['Daily AQI Value'] if 'Daily AQI Value' in data.columns else [])].resample('M').mean().reset_index()
        data = numeric_data

    # Ensure no missing data after aggregation
    data = data[[x_column, y_column]].dropna()

    # Plot button
    if st.button("Plot Graph"):
        # Create the plot
        fig, ax = plt.subplots()

        # Line Plot
        ax.plot(data[x_column], data[y_column], marker='o', linestyle='-', linewidth=1)
        ax.set_title(f"{y_column} vs {x_column} ({aggregation} Data)")

        # Set labels with the appropriate unit of measurement
        ax.set_xlabel(x_column)
        if y_column == "Measurement":
            ax.set_ylabel(f"Measurement ({unit_of_measurement})")
        elif y_column == "Daily AQI Value":
            ax.set_ylabel("Daily AQI Value")

        # Enhance readability
        ax.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=0.7)  # Add gridlines
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

        st.pyplot(fig)
        st.write(f"Displaying {aggregation.lower()} data. Original data was aggregated for clarity.")

except FileNotFoundError:
    st.error(f"The file '{file_name}' was not found. Ensure it is included in the repository.")

except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
