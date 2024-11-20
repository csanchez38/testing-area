import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title of the app
st.title("California Air Quality Trends")

# File selection
file_names = [f"California{year}.xlsx" for year in range(2019, 2025)]
selected_files = st.multiselect("Select files to compare", file_names, default=file_names)

if selected_files:
    try:
        # Extract years directly from filenames
        selected_years = [int(file.split("California")[1].split(".xlsx")[0]) for file in selected_files]

        # Combine data from selected files
        all_data = []
        for file_name in selected_files:
            # Extract the year from the file name
            year = file_name.split("California")[1].split(".xlsx")[0]
            
            # Read the data
            excel_data = pd.ExcelFile(file_name)
            sheet_names = excel_data.sheet_names

            # Dropdown to select the sheet (for the first file only, default to the first sheet for others)
            if len(all_data) == 0:
                selected_sheet = st.selectbox("Select a sheet to analyze", sheet_names)
            else:
                selected_sheet = sheet_names[0]  # Default to the first sheet for subsequent files

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

            # Add "Year" and "Month" columns
            data['Year'] = data['Date'].dt.year
            data['Month'] = data['Date'].dt.month

            # Append the data
            all_data.append(data)

        # Combine all the data into one DataFrame
        combined_data = pd.concat(all_data, ignore_index=True)

        # Ensure numeric columns are clean
        combined_data['Measurement'] = pd.to_numeric(combined_data['Measurement'], errors='coerce')
        combined_data['Daily AQI Value'] = pd.to_numeric(combined_data['Daily AQI Value'], errors='coerce')

        # Drop rows where 'Measurement' is missing
        combined_data = combined_data.dropna(subset=['Measurement'])

        # Extract the unit of measurement dynamically
        unit_of_measurement = combined_data['Units'].iloc[0] if 'Units' in combined_data.columns and not combined_data['Units'].isnull().all() else "Unknown Units"

        # Inform the user if the AQI column is missing or empty
        if combined_data['Daily AQI Value'].isnull().all():
            st.warning("The 'Daily AQI Value' column is empty or unavailable for this dataset. Only the 'Measurement' column is available for plotting.")
            available_y_columns = ['Measurement']
        else:
            available_y_columns = ['Measurement', 'Daily AQI Value']

        # Display a preview of the combined data
        st.write("Combined Data Preview:")
        st.dataframe(combined_data.head())

        # Dropdown for selecting Y-axis column
        y_column = st.selectbox("Select Y-axis column", available_y_columns)

        # Group data by Year and Month for the line graph
        monthly_data = combined_data.groupby(['Year', 'Month'])[y_column].mean().reset_index()

        # Plot button
        if st.button("Plot Graph"):
            # Create the line plot
            fig, ax = plt.subplots(figsize=(12, 6))
            for year in selected_years:
                year_data = monthly_data[monthly_data['Year'] == year]
                ax.plot(
                    year_data['Month'], 
                    year_data[y_column], 
                    marker='o', 
                    linestyle='-', 
                    label=str(year),
                    markersize=4,
                )
            ax.set_title(f"Monthly {y_column} Trends")
            ax.set_xlabel("Month")
            ax.set_ylabel(f"{y_column} ({unit_of_measurement})")
            ax.legend(title="Year", loc='upper left', bbox_to_anchor=(1, 1))
            ax.grid(True, linestyle='--', alpha=0.7)
            plt.xticks(ticks=range(1, 13), labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
            st.pyplot(fig)

    except FileNotFoundError:
        st.error(f"One or more selected files were not found. Ensure they are included in the repository.")

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
