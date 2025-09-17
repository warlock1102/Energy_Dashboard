from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import sys
import os

# Add the project root to Python path to import shared modules  
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.utils import ServiceRegistry
from shared.models import OptimizationRequest, MeterReading
from datetime import datetime
from typing import List

app = FastAPI(
    title="Energy Dashboard API Gateway",
    description="Central API Gateway for Energy Dashboard microservices",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"service": "Energy Dashboard API Gateway", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "gateway": "api-gateway"}


@app.get("/api/optimize/{household_id}")
async def optimize_household(household_id: int):
    """
    Optimize energy consumption for a household
    This endpoint maintains backward compatibility with the original API
    """
    try:
        # This would eventually call the household service to get data
        # For now, we'll simulate getting household data
        household_data = [
            MeterReading(
                household_id=household_id,
                timestamp=datetime.now(),
                consumption=1.5
            ),
            MeterReading(
                household_id=household_id,
                timestamp=datetime.now(),
                consumption=2.0
            )
        ]
        
        if not household_data:
            return {"schedule": [], "message": "No data yet for this household"}
        
        # Call optimization service
        optimization_client = ServiceRegistry.get_client("energy-optimization")
        
        # Prepare optimization request
        request_data = OptimizationRequest(
            household_id=household_id,
            household_data=household_data
        )
        
        # Call the optimization service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ServiceRegistry.get_service_url('energy-optimization')}/optimize",
                json=request_data.dict(),
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Optimization service error")
            
            result = response.json()
            
            # Transform response for backward compatibility
            return {
                "schedule": result.get("schedule", []),
                "message": result.get("message", "Optimization completed")
            }
    
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/optimize")
async def optimize_advanced(request: OptimizationRequest):
    """
    Advanced optimization endpoint with full request model
    """
    try:
        optimization_client = ServiceRegistry.get_client("energy-optimization")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ServiceRegistry.get_service_url('energy-optimization')}/optimize",
                json=request.dict(),
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Optimization service error")
            
            return response.json()
    
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Optimization service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/services/health")
async def check_all_services():
    """
    Check health of all microservices
    """
    service_status = {}
    
    for service_name in ServiceRegistry.SERVICES.keys():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{ServiceRegistry.get_service_url(service_name)}/health",
                    timeout=5.0
                )
                service_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds()
                }
        except Exception as e:
            service_status[service_name] = {
                "status": "unreachable",
                "error": str(e)
            }
    
    return {
        "gateway": "healthy",
        "services": service_status
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)