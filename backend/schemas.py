from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# --- Autenticación ---
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str

# --- Lecturas de Sensores ---
class SensorDataOut(BaseModel):
    id: int
    sensor_id: str
    timestamp: str
    value: float

    model_config = ConfigDict(from_attributes=True)

# --- Sensores ---
class SensorOut(BaseModel):
    id: str
    parcel_id: int
    type: str
    unit: str
    description: Optional[str] = None
    threshold_low: Optional[float] = None
    threshold_high: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

# --- Parcelas ---
class ParcelOut(BaseModel):
    id: int
    name: str
    location: str
    user_id: int
    sensors: List[SensorOut] = []

    model_config = ConfigDict(from_attributes=True)