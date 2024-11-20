import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# File names (in the same directory as app.py)
file_names = {
    "2024": "California2024.xlsx",
    "2023": "California2023.xlsx",
    "2022": "California2022.xlsx",
    "2021": "California2021.xlsx",
    "2020": "California2020.xlsx",
    "2019": "California2019.xlsx",
}

# Measurement information for each sheet
measurement_info = {
    "CO": "Measured in parts per million (ppm)",
    "Pb": "Measured in micrograms per cubic meter (µg/m³)",
    "NO2": "Measured in parts per billion (ppb)",
    "Ozone": "Measured in parts per million (ppm)",
    "PM2.5": "Measured in micrograms per cubic meter (µg/m³)",
}

# Function to load data
def load_data(file, sheet_name):
    try:
        # Read the sheet
        df = pd.read_excel(file, sheet_name=sheet_name)
        
        # Extract column B as the key measurement column
        measurement_col = df.columns[1]  # Assume column B is always the second column
        
        # Ensure the 'Date' column is properly parsed
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Ensure Date is datetime
        df = df.dropna(subset=['Date'])  # Drop invalid dates
        df['Month'] = df['Date'].dt.month  # Extract month
        df['Day'] = df['Date'].dt.day  # Extract day (for finer granularity)
        df['Year'] = df['Date'].dt.year  # Extract year
        return df, measurement_col
    except Exception as e:
        st.error(f"Error loading {sheet_name} from {file}: {e}")
        return pd.DataFrame(), None

# Streamlit app
st.title("California Air Quality Data Viewer")

# Sidebar for options
sheet_options = ["CO", "Pb", "NO2", "Ozone", "PM2.5"]
selected_sheet = st.sidebar.selectbox("Select Pollutant Sheet", sheet_options)

# Display measurement details for the selected sheet
st.sidebar.write(f"**Measurement Info**: {measurement_info[selected_sheet]}")

# Measurement type options
measurement_options = {"Measurement": "Measurement (column B)"}
if selected_sheet != "Pb":  # Only add AQI if not Pb
    measurement_options["AQI"] = "Daily AQI Value"

selected_measurement = st.sidebar.radio("Select Data Type", list(measurement_options.keys()))

# Year selection
all_years = list(file_names.keys())
selected_years = st.sidebar.multiselect("Select Years", all_years, default=all_years)

# Load and combine data
dataframes = []
measurement_column_name = None  # This will be dynamically set
for year, file in file_names.items():
    if year in selected_years:  # Only load selected years
        df, measurement_col = load_data(file, selected_sheet)
        if not df.empty:
            dataframes.append(df)
            # Set the measurement column name based on the first loaded file
            if measurement_column_name is None:
                measurement_column_name = measurement_col

if dataframes:
    all_data = pd.concat(dataframes, ignore_index=True)

    if selected_measurement == "AQI":
        measurement_column_name = "Daily AQI Value"

    if measurement_column_name not in all_data.columns:
        st.error(f"The selected measurement column '{measurement_column_name}' is not available in the {selected_sheet} sheet.")
    else:
        # Group data by Year and Month for comparison
        grouped_data = all_data.groupby(['Year', 'Month'])[measurement_column_name].mean().reset_index()

        # Line Plot for Year-to-Year Comparison
        st.subheader(f"{selected_sheet} Year-to-Year Comparison")
        line_fig, ax = plt.subplots(figsize=(10, 6))

        # Plot each year
        for year in grouped_data['Year'].unique():
            year_data = grouped_data[grouped_data['Year'] == year]
            ax.plot(
                year_data['Month'], 
                year_data[measurement_column_name], 
                label=f"{year}"
            )
        
        ax.set_title(f"Year-to-Year Comparison of {measurement_column_name} for {selected_sheet}")
        ax.set_xlabel("Month")
        ax.set_ylabel(measurement_column_name)
        ax.legend()
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        st.pyplot(line_fig)

        # Only show Bar Chart and Pie Chart if Measurement is selected
        if selected_measurement == "Measurement":
            # Bar Chart for Total Values by Year
            st.subheader(f"{selected_sheet} Total Values by Year")
            bar_data = all_data.groupby('Year')[measurement_column_name].sum().reset_index()
            bar_fig, ax = plt.subplots()
            ax.bar(bar_data['Year'], bar_data[measurement_column_name])
            ax.set_title(f"Total {measurement_column_name} by Year")
            ax.set_xlabel("Year")
            ax.set_ylabel(f"Total {measurement_column_name}")
            st.pyplot(bar_fig)

            # Pie Chart for Proportions by Year
            st.subheader(f"{selected_sheet} Proportion of Total Values by Year")
            pie_fig, ax = plt.subplots()
            ax.pie(bar_data[measurement_column_name], labels=bar_data['Year'], autopct='%1.1f%%', startangle=90)
            ax.set_title(f"Proportion of {measurement_column_name} by Year")
            st.pyplot(pie_fig)

        # Display grouped data
        st.subheader("Grouped Data (Monthly Averages)")
        st.write(grouped_data)
else:
    st.error("No data available. Please check the input files or selected sheet.")
