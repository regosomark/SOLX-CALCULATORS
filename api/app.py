import streamlit as st
import requests
import pandas as pd
from models.solar_calculator import SolarGuarantee

# Set the FastAPI endpoint
API_URL = "http://localhost:8000/calculate/solar_guarantee"

# Set page configuration to wide layout
st.set_page_config(layout="wide")

def main():
    st.title("Solar Guarantee Calculator")

    # Form to input data
    with st.form(key='solar_guarantee_form'):
        client_id = st.number_input("Client ID", min_value=1, step=1)
        solar_rate = st.number_input("Solar Rate (pHp)", min_value=0.0, step=0.01)
        line_rental = st.number_input("Line Rental (pHp)", min_value=0.0, step=0.01, value=0.0)
        threshold = st.number_input("Threshold (kW)", min_value=0.0, step=0.01, value=0.0)
        admin_fee = st.number_input("Admin Fee (pHp)", min_value=0.0, step=0.01, value=0.0)

        # Default solar guarantee percentages
        default_solar_guarantee = {
            'Hour': list(range(1, 25)),
            'Solar Guarantee (%)': [0, 0, 0, 0, 0, 0, 0, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 0, 0, 0, 0, 0, 0, 0]
        }
        solar_guarantee_df = pd.DataFrame(default_solar_guarantee)

        # Transpose the DataFrame for horizontal display
        solar_guarantee_df_t = solar_guarantee_df.set_index('Hour').T

        st.write('Solar Guarantee Percentage Table:')
        edited_df_t = st.data_editor(solar_guarantee_df_t, num_rows="fixed", use_container_width=True)

        # Convert the edited DataFrame back to a list for submission
        solar_guarantee_percentage = edited_df_t.loc['Solar Guarantee (%)'].tolist()

        # Validate solar guarantee percentages
        invalid_values = [value for value in solar_guarantee_percentage if value < 0 or value > 100]

        # Submit button
        submit_button = st.form_submit_button("Calculate")

        # If the button is clicked, check for errors
        if submit_button:
            if invalid_values:
                st.error("Error: Solar Guarantee Percentages must be between 0 and 100. Invalid values: {}".format(invalid_values))
            else:
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

                    # Change Supply_Period format to mm-yy
                    results_df['Supply_Period'] = pd.to_datetime(results_df['Supply_Period']).dt.strftime('%b-%y')

                    st.subheader("Calculation Results")
                    st.dataframe(results_df)

                except requests.exceptions.RequestException as e:
                    st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
