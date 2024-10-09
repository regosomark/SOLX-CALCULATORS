from pydantic import BaseModel
from typing import List

class SolarGuarantee(BaseModel):
    client_id: int  # Changed to a single client ID
    solar_rate: float
    line_rental: float = 0.0
    threshold: float = 0.0
    solar_guarantee_percentage: List[float]  # List of solar guarantee percentages (1-24 hours)
    admin_fee: float = 0.0
