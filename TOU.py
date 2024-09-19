import streamlit as st
import pandas as pd
import io
 
# Set page configuration for full width
st.set_page_config(layout="wide")
 
# Step 1: Upload Load Profile
st.title("Time of Use Calculator")
uploaded_file = st.file_uploader("Upload Load Profile (Processed LP with WESM Rates)", type=["csv", "xlsx"])
 
if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
 
    # Handle 'kWh' column
    if 'kWh' in df.columns:
        kwh_column = 'kWh'
    elif len(df.columns) >= 8:
        kwh_column = df.columns[7]  # 8th column
    else:
        st.error("The data does not contain a 'kWh' column and does not have an 8th column.")
   
    # Display the load profile data in an expandable section with scrollbars
    with st.expander("Load Profile Data", expanded=True):
        st.dataframe(df, use_container_width=True, hide_index=True, height=500)
 
    # Step 2: Handle 'date' column
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df.iloc[:, 2])  # Convert the third column to datetime
 
        # Compute the supply period based on the date range logic
        def calculate_supply_period(date):
            if date.day >= 26:
                return (date + pd.DateOffset(months=1)).strftime('%b-%y')
            else:
                return date.strftime('%b-%y')
 
        df['Supply Period'] = df['date'].apply(calculate_supply_period)
    else:
        st.error("The data does not contain a 'date' column.")
 
    # Step 3: Single Slider for Peak Hours Range (default range 0-23)
    peak_hours = st.slider("Select Peak Hours Range", 0, 23, (8, 21))
    peak_start, peak_end = peak_hours
 
    # Filter based on the 'correct hour' column
    df['Peak'] = df['correct hour'].apply(lambda x: peak_start <= x <= peak_end)
 
    # Group by supply period to calculate metrics per supply period
    monthly_data = df.groupby('Supply Period').agg(
        total_consumption_kwh=(kwh_column, 'sum'),
        actual_peak_kwh=(kwh_column, lambda x: x[df['Peak']].sum()),
        actual_off_peak_kwh=(kwh_column, lambda x: x[~df['Peak']].sum())
    ).reset_index()
 
    # Convert 'Supply Period' back to datetime for sorting purposes
    monthly_data['Supply Period'] = pd.to_datetime(monthly_data['Supply Period'], format='%b-%y')
 
    # Step 4: Input Buttons for Rates with default values
    peak_rate = st.number_input("Peak Hours Rate (PhP/kWh):", min_value=0.0, value=6.0)
    off_peak_rate = st.number_input("Off-Peak Hours Rate (PhP/kWh):", min_value=0.0, value=5.5)
 
    # Step 5: Calculate Costs
    monthly_data['actual_peak_php'] = monthly_data['actual_peak_kwh'] * peak_rate
    monthly_data['actual_off_peak_php'] = monthly_data['actual_off_peak_kwh'] * off_peak_rate
    monthly_data['monthly_cost_php'] = monthly_data['actual_peak_php'] + monthly_data['actual_off_peak_php']
    monthly_data['effective_rate'] = monthly_data['monthly_cost_php'] / monthly_data['total_consumption_kwh']
 
    # Step 6: Sort by 'Supply Period' to ensure chronological order
    monthly_data = monthly_data.sort_values(by='Supply Period').reset_index(drop=True)
 
    # Convert 'Supply Period' back to string for final display
    monthly_data['Supply Period'] = monthly_data['Supply Period'].dt.strftime('%b-%y')
 
    # Create DataFrame for Output
    results_df = monthly_data[['Supply Period', 'total_consumption_kwh', 'actual_peak_kwh', 'actual_peak_php',
                               'actual_off_peak_kwh', 'actual_off_peak_php', 'monthly_cost_php', 'effective_rate']]
    results_df.columns = ["Supply Period", "Total Consumption (kWh)", "Actual Peak (kWh)", "Actual Peak (PhP)",
                          "Actual Off-Peak (kWh)", "Actual Off-Peak (PhP)", "Monthly Cost (PhP)", "Effective Rate (PhP/kWh)"]
 
    # Step 7: Add Total and Average Row
    total_row = results_df.sum(numeric_only=True)
    total_row["Supply Period"] = "Total"
    total_row["Effective Rate (PhP/kWh)"] = total_row["Monthly Cost (PhP)"] / total_row["Total Consumption (kWh)"]
 
    average_row = results_df.mean(numeric_only=True)
    average_row["Supply Period"] = "Average"
 
    # Use pd.concat to add total and average rows
    results_df = pd.concat([results_df, pd.DataFrame([total_row, average_row])], ignore_index=True)
 
    # Remove empty rows (if any exist)
    results_df = results_df.dropna(how='all')
 
    # Display the final results table with full width and no index
    st.write("Final Results:")
    st.dataframe(results_df, use_container_width=True, hide_index=True)
 
    # Step 8: Download button for final results as Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        results_df.to_excel(writer, index=False, sheet_name='Final Results')
 
    st.download_button(
        label="Download",
        data=output.getvalue(),
        file_name='final_results.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )