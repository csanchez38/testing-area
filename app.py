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

# Function to load data
def load_data(file, sheet_name):
    try:
        df = pd.read_excel(file, sheet_name=sheet_name)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Ensure Date is datetime
        df = df.dropna(subset=['Date'])  # Drop invalid dates
        df['Month'] = df['Date'].dt.month  # Extract month
        df['Day'] = df['Date'].dt.day  # Extract day (for finer granularity)
        df['Year'] = df['Date'].dt.year  # Extract year
        return df
    except Exception as e:
        st.error(f"Error loading {sheet_name} from {file}: {e}")
        return pd.DataFrame()

# Streamlit app
st.title("Year-to-Year Comparison for California Air Quality Data")

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
for year, file in file_names.items():
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
        # Group data by Year and Month for comparison
        grouped_data = all_data.groupby(['Year', 'Month'])[measurement_column].mean().reset_index()

        # Line Plot for Year-to-Year Comparison
        st.subheader(f"{selected_sheet} Year-to-Year Comparison")
        line_fig, ax = plt.subplots(figsize=(10, 6))

        # Plot each year
        for year in grouped_data['Year'].unique():
            year_data = grouped_data[grouped_data['Year'] == year]
            ax.plot(
                year_data['Month'], 
                year_data[measurement_column], 
                label=f"{year}"
            )
        
        ax.set_title(f"Year-to-Year {selected_measurement} Comparison for {selected_sheet}")
        ax.set_xlabel("Month")
        ax.set_ylabel(selected_measurement)
        ax.legend()
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        st.pyplot(line_fig)

        # Display grouped data
        st.subheader("Grouped Data (Monthly Averages)")
        st.write(grouped_data)
else:
    st.error("No data available. Please check the input files or selected sheet.")
