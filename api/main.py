import sys
import os
from fastapi import FastAPI, HTTPException
import pandas as pd
from calculator.solar_calculator import solar_guarantee_calculator
from models.solar_calculator import SolarGuarantee
from utils import connect_database, fetch_effective_rates

# Add the current directory to the system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI()

@app.post("/calculate/solar_guarantee")
async def calculate_solar_guarantee(params: SolarGuarantee):
    # Check if client IDs are provided
    if not params.client_ids:
        raise HTTPException(status_code=400, detail="No client IDs provided")
    
    # Connect to the database
    conn = connect_database()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")
    
    # Fetch client data
    data = fetch_effective_rates(conn, params.client_ids)
    if data is None or data.empty:
        raise HTTPException(status_code=404, detail="No data found for the provided client IDs")
    
    # Call the calculator with the provided input parameters
    try:
        result = solar_guarantee_calculator(data, 
                                            params.solar_rate, 
                                            params.line_rental, 
                                            params.threshold, 
                                            params.solar_guarantee_percentage, 
                                            params.admin_fee)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Close the database connection
    conn.close()

    # Return the result as JSON
    return {"status": "success", "data": result.to_dict(orient='records')}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
