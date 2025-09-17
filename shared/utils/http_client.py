import httpx
import os
from typing import Dict, Any, Optional
import asyncio
import json


class ServiceClient:
    """HTTP client for inter-service communication"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request to another service"""
        url = f"{self.base_url}{endpoint}"
        async with self.client as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request to another service"""
        url = f"{self.base_url}{endpoint}"
        async with self.client as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            return response.json()
    
    def close(self):
        """Close the HTTP client"""
        asyncio.create_task(self.client.aclose())


class ServiceRegistry:
    """Registry for service URLs"""
    
    SERVICES = {
        "energy-optimization": os.getenv("OPTIMIZATION_SERVICE_URL", "http://energy-optimization:8000"),
        "data-ingestion": os.getenv("DATA_INGESTION_SERVICE_URL", "http://data-ingestion:8000"),
        "household": os.getenv("HOUSEHOLD_SERVICE_URL", "http://household:8000"),
        "weather-pv": os.getenv("WEATHER_PV_SERVICE_URL", "http://weather-pv:8000"),
        "iot": os.getenv("IOT_SERVICE_URL", "http://iot:8000"),
    }
    
    @classmethod
    def get_client(cls, service_name: str) -> ServiceClient:
        """Get HTTP client for a specific service"""
        if service_name not in cls.SERVICES:
            raise ValueError(f"Unknown service: {service_name}")
        
        return ServiceClient(cls.SERVICES[service_name])
    
    @classmethod
    def get_service_url(cls, service_name: str) -> str:
        """Get URL for a specific service"""
        if service_name not in cls.SERVICES:
            raise ValueError(f"Unknown service: {service_name}")
        
        return cls.SERVICES[service_name]