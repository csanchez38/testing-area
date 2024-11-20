import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# File paths
file_paths = {
    "2024": "/mnt/data/California2024.xlsx",
    "2023": "/mnt/data/California2023.xlsx",
    "2022": "/mnt/data/California2022.xlsx",
    "2021": "/mnt/data/California2021.xlsx",
    "2020": "/mnt/data/California2020.xlsx",
    "2019": "/mnt/data/California2019.xlsx",
}

# Function to load data
def load_data(file, sheet_name):
    try:
        df = pd.read_excel(file, sheet_name=sheet_name)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Ensure Date is datetime
        df = df.dropna(subset=['Date'])  # Drop invalid dates
        df = df.sort_values('Date')  # Sort by Date
        df['Year'] = df['Date'].dt.year  # Extract Year for comparison
        return df
    except Exception as e:
        st.error(f"Error loading {sheet_name} from {file}: {e}")
        return pd.DataFrame()

# Streamlit app
st.title("California Air Quality Data Viewer")

# Sidebar for options
sheet_options = ["CO", "Pb", "NO2", "Ozone", "PM2.5"]
selected_sheet = st.sidebar.selectbox("Select Pollutant Sheet", sheet_options)

measurement_options = {
    "Measurement": "Daily Max 8-hour CO Concentration",  # Adjust for other sheets if needed
    "AQI": "Daily AQI Value",
}
selected_measurement = st.sidebar.selectbox("Select Measurement Type", measurement_options.keys())

# Load and combine data
dataframes = []
for year, file in file_paths.items():
    df = load_data(file, selected_sheet)
    if not df.empty:
        dataframes.append(df)

if dataframes:
    all_data = pd.concat(dataframes, ignore_index=True)

    # Filtered column
    measurement_column = measurement_options[selected_measurement]
    if measurement_column not in all_data.columns:
        st.error(f"The selected measurement type '{measurement_column}' is not available in the {selected_sheet} sheet.")
    else:
        # Sidebar for year filtering
        year_options = sorted(all_data['Year'].unique())
        selected_years = st.sidebar.multiselect("Select Years to Compare", year_options, default=year_options)

        filtered_data = all_data[all_data['Year'].isin(selected_years)]

        # Line Plot
        st.subheader("Line Plot: Data Comparison Over Time")
        line_fig, ax = plt.subplots()
        for year in selected_years:
            year_data = filtered_data[filtered_data['Year'] == year]
            ax.plot(year_data['Date'], year_data[measurement_column], label=str(year))
        ax.set_title(f"{selected_sheet} Data Comparison Over Time")
        ax.set_xlabel("Date")
        ax.set_ylabel(selected_measurement)
        ax.legend()
        st.pyplot(line_fig)

        # Bar Graph
        st.subheader("Bar Graph: Data Comparison")
        bar_fig, ax = plt.subplots()
        bar_data = filtered_data.groupby('Year')[measurement_column].sum().reset_index()
        ax.bar(bar_data['Year'], bar_data[measurement_column])
        ax.set_title(f"Total {selected_measurement} by Year")
        ax.set_xlabel("Year")
        ax.set_ylabel(f"Total {selected_measurement}")
        st.pyplot(bar_fig)

        # Pie Chart
        st.subheader("Pie Chart: Data Proportion by Year")
        pie_data = bar_data.copy()
        pie_fig, ax = plt.subplots()
        ax.pie(pie_data[measurement_column], labels=pie_data['Year'], autopct='%1.1f%%', startangle=90)
        ax.set_title(f"Proportion of {selected_measurement} by Year")
        st.pyplot(pie_fig)

        # Display filtered data
        st.subheader("Filtered Data")
        st.write(filtered_data)
else:
    st.error("No data available. Please check the input files or selected sheet.")
