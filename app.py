try:
    # Read the Excel file and list available sheets
    excel_data = pd.ExcelFile(file_name)
    sheet_names = excel_data.sheet_names

    # Dropdown to select the sheet
    selected_sheet = st.selectbox("Select a sheet to analyze", sheet_names)

    # Read the selected sheet into a DataFrame
    data = pd.read_excel(file_name, sheet_name=selected_sheet)

    # Debugging info: Show column names
    st.write("Columns in the data:", data.columns.tolist())

    # Check for required columns
    required_columns = ['Date', 'Daily Mean']
    if not all(col in data.columns for col in required_columns):
        st.error(f"Required columns are missing: {', '.join([col for col in required_columns if col not in data.columns])}")
    else:
        # Filter rows where 'Date' or 'Daily Mean' are missing
        data = data.dropna(subset=required_columns)

        # Convert 'Date' column to datetime
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
        data = data.dropna(subset=['Date'])

        # Debugging info: Show filtered data
        st.write("Filtered Data Preview:")
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

except FileNotFoundError:
    st.error("The file 'California2019.xlsx' was not found. Ensure it is included in the repository.")
