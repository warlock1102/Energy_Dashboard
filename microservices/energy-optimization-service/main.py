from fastapi import FastAPI, HTTPException
from typing import List
import sys
import os

# Add the project root to Python path to import shared modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.models import OptimizationRequest, OptimizationResponse, EnergySchedule
from optimization_engine import OptimizationEngine

app = FastAPI(
    title="Energy Optimization Service",
    description="Microservice for household energy optimization and battery scheduling",
    version="1.0.0"
)

# Initialize optimization engine
optimizer = OptimizationEngine()


@app.get("/")
def root():
    return {"service": "Energy Optimization Service", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "energy-optimization"}


@app.post("/optimize", response_model=OptimizationResponse)
def optimize_energy(request: OptimizationRequest):
    """
    Optimize energy consumption and battery scheduling for a household
    """
    try:
        if not request.household_data:
            return OptimizationResponse(
                household_id=request.household_id,
                schedule=[],
                message="No data provided for optimization"
            )
        
        # Convert household data for optimization engine
        household_data = [
            {
                "household_id": reading.household_id,
                "timestamp": reading.timestamp.isoformat(),
                "consumption": reading.consumption
            }
            for reading in request.household_data
        ]
        
        # Run optimization
        schedule_data = optimizer.optimize_energy(household_data)
        
        # Convert back to response model
        schedule = [
            EnergySchedule(
                charge=item["charge"],
                discharge=item["discharge"]
            )
            for item in schedule_data
        ]
        
        return OptimizationResponse(
            household_id=request.household_id,
            schedule=schedule,
            message=f"Optimization completed for {len(schedule)} time slots"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@app.post("/optimize/simple")
def optimize_simple(household_data: List[dict]):
    """
    Simple optimization endpoint for backward compatibility
    """
    try:
        schedule = optimizer.optimize_energy(household_data)
        return {"schedule": schedule}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)