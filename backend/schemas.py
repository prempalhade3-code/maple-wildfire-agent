from pydantic import BaseModel, Field
from typing import List, Optional

class TransmissionLineOut(BaseModel):
    id: int
    name: str
    voltage_kv: Optional[float] = None
    # geometry is not sent; front‑end will request GeoJSON separately if needed
    class Config:
        orm_mode = True

class RiskScoreOut(BaseModel):
    line_id: int
    score: float = Field(..., description="Overall risk score (0‑100)")
    probability: float = Field(..., description="Ignition probability (0‑1)")
    consequence: float = Field(..., description="Consequence factor (0‑1)")
    timestamp: str
    
    # Live telemetry data
    wind_speed: Optional[float] = None
    wind_direction: Optional[int] = None
    humidity: Optional[float] = None
    temperature: Optional[float] = None
    soil_moisture: Optional[float] = None
    canopy_density: Optional[float] = None
    slope: Optional[float] = None
    distance: Optional[float] = None
    building_count: Optional[int] = None
    contributions: Optional[dict] = None
    citations: Optional[List[dict]] = None
    evidence: Optional[List[dict]] = None
    decision: Optional[dict] = None
    decision_timeline: Optional[List[dict]] = None
    data_mode: Optional[str] = None

    class Config:
        from_attributes = True
        orm_mode = True

class ActuationRequest(BaseModel):
    line_id: int
    action: str = Field(..., description="Action to perform, e.g., 'shutdown'")

class ActuationResponse(BaseModel):
    status: str
    detail: Optional[str] = None
