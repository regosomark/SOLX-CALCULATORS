import streamlit as st
import requests
import pandas as pd
from model import SolarGuarantee

# Set the FastAPI endpoint
API_URL = "http://localhost:8000/calculate/solar_guarantee"

def main():
    st.title("Solar Guarantee Calculator")

    # Form to input data
    with st.form(key='solar_guarantee_form'):
        client_id = st.number_input("Client ID", min_value=1, step=1)
        solar_rate = st.number_input("Solar Rate (pHp)", min_value=0.0, step=0.01)
        line_rental = st.number_input("Line Rental (pHp)", min_value=0.0, step=0.01, value=0.0)
        threshold = st.number_input("Threshold (kW)", min_value=0.0, step=0.01, value=0.0)
        admin_fee = st.number_input("Admin Fee (pHp)", min_value=0.0, step=0.01, value=0.0)

        # Input solar guarantee percentages for 24 hours
        solar_guarantee_percentage = []
        for hour in range(1, 25):
            percentage = st.number_input(f"Solar Guarantee Percentage for Hour {hour} (%)", min_value=0.0, max_value=100.0, step=0.1, value=0.0)
            solar_guarantee_percentage.append(percentage)

        # Submit button
        submit_button = st.form_submit_button("Calculate")

        if submit_button:
            # Create request body
            request_data = SolarGuarantee(
                client_id=client_id,
                solar_rate=solar_rate,
                line_rental=line_rental,
                threshold=threshold,
                solar_guarantee_percentage=solar_guarantee_percentage,
                admin_fee=admin_fee
            )

            # Send request to FastAPI backend
            try:
                response = requests.post(API_URL, json=request_data.dict())
                response.raise_for_status()  # Raise an error for bad responses
                results = response.json()

                # Convert results to DataFrame for display
                results_df = pd.DataFrame(results)
                st.subheader("Calculation Results")
                st.dataframe(results_df)

            except requests.exceptions.RequestException as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
