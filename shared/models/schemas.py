from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class MeterReading(BaseModel):
    household_id: int
    timestamp: datetime
    consumption: float


class PVForecast(BaseModel):
    timestamp: datetime
    pv_output: float


class WeatherForecast(BaseModel):
    timestamp: datetime
    temperature: float
    irradiation: float


class IoTData(BaseModel):
    time: datetime
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    energy_kwh: Optional[float] = None
    room: str
    device_id: str


class EnergySchedule(BaseModel):
    charge: float
    discharge: float
    timestamp: Optional[datetime] = None


class OptimizationRequest(BaseModel):
    household_id: int
    household_data: List[MeterReading]


class OptimizationResponse(BaseModel):
    household_id: int
    schedule: List[EnergySchedule]
    message: Optional[str] = None