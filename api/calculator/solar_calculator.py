import pandas as pd
from utils import get_supply_period  # Import the utility function

def solar_guarantee_calculator(data, solar_rate, line_rental=0, threshold=0, solar_guarantee_percentage=None, admin_fee=0):
    if solar_guarantee_percentage is None:
        solar_guarantee_percentage = [0.0] * 24  # Default to 0% if not provided

    # Ensure that the 'hour' column has valid values
    if data['hour'].max() > 24 or data['hour'].min() < 1:
        raise ValueError("Hour values in the 'hour' column must be between 1 and 24.")
    
    # Initialize columns
    data['Solar_Consumption_kw'] = 0.0
    data['Non_Solar_Consumption_kw'] = 0.0
    data['Solar_Charge_pHp'] = 0.0
    data['Non_Solar_Charge_pHp'] = 0.0
    data['Total_Charge_pHp'] = 0.0

    # Calculate solar and non-solar consumption and charges
    for index, row in data.iterrows():
        hour = int(row['hour'])
        kw = row['kw']
        wesm = row['wesm']

        # Get the solar guarantee percentage for the current hour
        solar_percentage = solar_guarantee_percentage[hour - 1]  

        # Calculate solar consumption
        Solar_Consumption_kw = kw * (solar_percentage / 100)

        # Apply threshold logic
        if threshold > 0:
            if Solar_Consumption_kw > threshold:
                Non_Solar_Consumption_kw = kw - threshold
                Solar_Consumption_kw = threshold
            else:
                Non_Solar_Consumption_kw = kw - Solar_Consumption_kw
        else:
            Non_Solar_Consumption_kw = kw - Solar_Consumption_kw

        # Calculate charges
        Solar_Charge_pHp = Solar_Consumption_kw * (solar_rate + line_rental)
        Non_Solar_Charge_pHp = Non_Solar_Consumption_kw * (wesm + admin_fee)

        # Update DataFrame
        data.at[index, 'Solar_Consumption_kw'] = Solar_Consumption_kw
        data.at[index, 'Non_Solar_Consumption_kw'] = Non_Solar_Consumption_kw
        data.at[index, 'Solar_Charge_pHp'] = Solar_Charge_pHp
        data.at[index, 'Non_Solar_Charge_pHp'] = Non_Solar_Charge_pHp
        data.at[index, 'Total_Charge_pHp'] = Solar_Charge_pHp + Non_Solar_Charge_pHp

    # Ensure datetime column exists and is of correct type
    if 'datetime' not in data.columns or not pd.api.types.is_datetime64_any_dtype(data['datetime']):
        raise ValueError("The 'datetime' column is missing or not in datetime format.")

    # Supply Period Calculation
    data['Supply_Period'], _ = zip(*data['datetime'].apply(get_supply_period))

    # Convert Supply_Period to a datetime format for sorting
    data['Supply_Period'] = pd.to_datetime(data['Supply_Period'], format='%b-%y')

    # Summary Pivot Table (Aggregated by Supply Period)
    pivot_df = data.pivot_table(
        index=['Supply_Period'],
        values=['kw', 'Solar_Consumption_kw', 'Solar_Charge_pHp', 
                'Non_Solar_Consumption_kw', 'Non_Solar_Charge_pHp', 'Total_Charge_pHp'],
        aggfunc='sum'
    ).reset_index()

    # Calculate Effective Rate (pHp/kw) for each supply period
    pivot_df['Effective_Rate'] = pivot_df['Total_Charge_pHp'] / pivot_df['kw']

    return pivot_df
