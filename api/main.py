from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from utils import connect_database, fetch_effective_rates
from calculator.solar_calculator import solar_guarantee_calculator

app = FastAPI()

class SolarGuaranteeRequest(BaseModel):
    client_id: int
    solar_rate: float
    line_rental: float = 0.0
    threshold: float = 0.0
    solar_guarantee_percentage: List[float]
    admin_fee: float = 0.0

@app.post("/calculate/solar_guarantee")
async def calculate_solar_guarantee(request: SolarGuaranteeRequest):
    conn = connect_database()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection error")

    try:
        # Fetch data for the specific client
        data = fetch_effective_rates(conn, [request.client_id])
        if data is None or data.empty:
            raise HTTPException(status_code=404, detail="No data found for the provided client ID")

        # Call the solar guarantee calculator
        summary = solar_guarantee_calculator(
            data,
            request.solar_rate,
            request.line_rental,
            request.threshold,
            request.solar_guarantee_percentage,
            request.admin_fee
        )
        
        return summary.to_dict(orient='records')

    finally:
        conn.close()
