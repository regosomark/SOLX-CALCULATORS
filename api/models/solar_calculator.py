from pydantic import BaseModel
from typing import List

class SolarGuarantee(BaseModel):
    solar_rate: float
    line_rental: float = 0.0
    admin_fee: float = 0.0
    threshold: float = 0.0
    solar_guarantee_percentage: List[float]  # List of solar guarantee percentages (1-24 hours)
    client_ids: List[int] = None  # List of client IDs to filter data
