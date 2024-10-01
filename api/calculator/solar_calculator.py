import pandas as pd

def solar_guarantee_calculator(data, solar_rate, line_rental=0, threshold=0, solar_guarantee_percentage=None, admin_fee=0):
    if solar_guarantee_percentage is None:
        solar_guarantee_percentage = [0.0] * 24  # Default to 0% if not provided

    # Ensure that the 'hour' column has valid values
    if data['hour'].max() > 24 or data['hour'].min() < 1:
        raise ValueError("Hour values in the 'hour' column must be between 1 and 24.")
    
    # Map solar guarantee percentage per hour from the input list
    data['solar_percentage'] = data['hour'].apply(lambda x: solar_guarantee_percentage[x - 1])
    
    # Calculate solar consumption
    data['solar_consumption'] = data.apply(
        lambda row: min(row['kwh'] * (row['solar_percentage'] / 100), threshold), 
        axis=1
    )
    
    # Calculate non-solar consumption
    data['non_solar_consumption'] = data['kwh'] - data['solar_consumption']
    
    # Calculate solar charge
    data['solar_charge'] = data['solar_consumption'] * (solar_rate + line_rental)
    
    # Calculate non-solar charge
    data['non_solar_charge'] = data['non_solar_consumption'] * (data['wesm'] + admin_fee)
    
    # Calculate total charge
    data['total_charge'] = data['solar_charge'] + data['non_solar_charge']
    
    # Calculate effective rate
    data['effective_rate'] = data['total_charge'] / data['kwh']
    
    return data
