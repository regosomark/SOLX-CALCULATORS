import pandas as pd
from utils import get_supply_period  # Import the utility function

def solar_guarantee_calculator(data, solar_rate, line_rental=0, threshold=0, solar_guarantee_percentage=None, admin_fee=0):
    if solar_guarantee_percentage is None:
        solar_guarantee_percentage = [0.0] * 24  # Default to 0% if not provided

    # Ensure that the 'hour' column has valid values
    if data['hour'].max() > 24 or data['hour'].min() < 1:
        raise ValueError("Hour values in the 'hour' column must be between 1 and 24.")
    
    # Map solar guarantee percentage per hour from the input list
    data['solar_percentage'] = data['hour'].apply(lambda x: solar_guarantee_percentage[x - 1])
    
    # Validate Solar Guarantee Percentages (between 0 and 100)
    data['solar_percentage'] = data['solar_percentage'].clip(0, 100)
    
    # Calculate solar consumption
    data['Solar_Consumption_kw'] = data.apply(
        lambda row: min(row['kw'] * (row['solar_percentage'] / 100), threshold), 
        axis=1
    )
    
    # Calculate non-solar consumption
    data['Non_Solar_Consumption_kw'] = data['kw'] - data['Solar_Consumption_kw']
    
    # Calculate solar charge
    data['Solar_Charge_pHp'] = data['Solar_Consumption_kw'] * (solar_rate + line_rental)
    
    # Calculate non-solar charge
    data['Non_Solar_Charge_pHp'] = data['Non_Solar_Consumption_kw'] * (data['wesm'] + admin_fee)
    
    # Calculate total charge
    data['Total_Charge_pHp'] = data['Solar_Charge_pHp'] + data['Non_Solar_Charge_pHp']
    
    # Calculate effective rate
    data['Effective_Rate'] = data['Total_Charge_pHp'] / data['kw']
    
    # Ensure datetime column exists and is of correct type
    if 'datetime' not in data.columns or not pd.api.types.is_datetime64_any_dtype(data['datetime']):
        raise ValueError("The 'datetime' column is missing or not in datetime format.")
    
    # Supply Period Calculation
    data['Supply_Period'], _ = zip(*data['datetime'].apply(get_supply_period))

    # Summary Pivot Table (Aggregated by Supply Period)
    pivot_df = data.pivot_table(
        index=['Supply_Period'],
        values=['kw', 'Solar_Consumption_kw', 'Solar_Charge_pHp', 'Non_Solar_Consumption_kw', 'Non_Solar_Charge_pHp', 'Total_Charge_pHp'],
        aggfunc='sum'
    ).reset_index()

    # Calculate Effective Rate (pHp/kw) for each supply period
    pivot_df['Effective_Rate'] = pivot_df['Total_Charge_pHp'] / pivot_df['kw']

    return pivot_df
