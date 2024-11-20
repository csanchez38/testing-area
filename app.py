# Dropdowns for selecting columns
x_column = st.selectbox("Select X-axis column", ['Date'])
y_column = st.selectbox("Select Y-axis column", ['Daily Mean', 'Daily AQI Value'])

# Dropdown for graph type
graph_type = st.selectbox(
    "Select Graph Type",
    ["Line", "Scatter", "Bar"]
)

# Add options for data aggregation
aggregation = st.selectbox(
    "Select Aggregation Level",
    ["None", "Weekly", "Monthly"]
)

# Plot button
if st.button("Plot Graph"):
    fig, ax = plt.subplots()

    # Resample data if aggregation is selected
    if aggregation == "Weekly":
        data = data.resample('W', on='Date').mean().reset_index()
    elif aggregation == "Monthly":
        data = data.resample('M', on='Date').mean().reset_index()

    # Line Plot
    if graph_type == "Line":
        ax.plot(data[x_column], data[y_column], marker='o', linestyle='-', linewidth=1)
        ax.set_title(f"{y_column} vs {x_column} (Line Plot)")

    # Scatter Plot
    elif graph_type == "Scatter":
        ax.scatter(data[x_column], data[y_column], s=10)
        ax.set_title(f"{y_column} vs {x_column} (Scatter Plot)")

    # Bar Plot
    elif graph_type == "Bar":
        ax.bar(data[x_column], data[y_column], width=10)
        ax.set_title(f"{y_column} vs {x_column} (Bar Chart)")

    # Enhance readability
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    ax.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=0.7)  # Add gridlines
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

    st.pyplot(fig)
    st.write("Tip: Use aggregation to clean up noisy daily data.")
