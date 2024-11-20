import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load Excel files
uploaded_files = [
    "California2024.xlsx",
    "California2023.xlsx",
    "California2022.xlsx",
    "California2021.xlsx",
    "California2020.xlsx",
    "California2019.xlsx",
]

# Helper function to load and process each file
def load_data(file):
    try:
        df = pd.read_excel(file)
        # Check for required columns
        if 'Date' not in df.columns or 'Value' not in df.columns:
            st.error(f"Missing required columns in {file}: Ensure 'Date' and 'Value' columns exist.")
            return pd.DataFrame()  # Return empty DataFrame for missing columns
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Ensure Date is in datetime format
        df = df.dropna(subset=['Date'])  # Drop rows with invalid dates
        df = df.sort_values('Date')  # Sort by Date
        df['Year'] = df['Date'].dt.year  # Extract Year for comparison
        return df
    except Exception as e:
        st.error(f"Error loading {file}: {e}")
        return pd.DataFrame()

# Load and combine data
all_data = pd.concat([load_data(file) for file in uploaded_files], ignore_index=True)

if all_data.empty:
    st.error("No valid data available. Please check the input files.")
else:
    # Streamlit app
    st.title("California Data Visualization and Comparison")

    # Sidebar for filtering
    year_options = sorted(all_data['Year'].unique())
    selected_years = st.sidebar.multiselect("Select Years to Compare", year_options, default=year_options)

    filtered_data = all_data[all_data['Year'].isin(selected_years)]

    # Line Plot
    st.subheader("Line Plot: Data Comparison Over Time")
    line_fig, ax = plt.subplots()
    for year in selected_years:
        year_data = filtered_data[filtered_data['Year'] == year]
        if not year_data.empty:
            ax.plot(year_data['Date'], year_data['Value'], label=str(year))
    ax.set_title("Data Comparison Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")
    ax.legend()
    st.pyplot(line_fig)

    # Bar Graph
    st.subheader("Bar Graph: Data Comparison")
    bar_fig, ax = plt.subplots()
    bar_data = filtered_data.groupby('Year')['Value'].sum().reset_index()
    ax.bar(bar_data['Year'], bar_data['Value'])
    ax.set_title("Total Value by Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Total Value")
    st.pyplot(bar_fig)

    # Pie Chart
    st.subheader("Pie Chart: Data Proportion by Year")
    pie_data = bar_data.copy()
    pie_fig, ax = plt.subplots()
    ax.pie(pie_data['Value'], labels=pie_data['Year'], autopct='%1.1f%%', startangle=90)
    ax.set_title("Proportion of Values by Year")
    st.pyplot(pie_fig)

    # Display filtered data
    st.subheader("Filtered Data")
    st.write(filtered_data)
