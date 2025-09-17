# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is an **Energy Information System (IS)** for households and residential areas that implements both monolithic and microservices architectures. The system optimizes energy demand, PV generation, battery storage, and flexible appliances with FastAPI backend, PostgreSQL database, and Grafana visualization.

## Architecture

The codebase supports two deployment patterns:

### Monolithic (Original)
- Single FastAPI application (`main.py`)
- ETL processes in background threads (`etl/batch.py`, `etl/streaming.py`) 
- Optimization logic (`optimization/scheduler.py`)
- Single database (`utils/db.py`)

### Microservices (New)
- **API Gateway**: Central entry point (`microservices/api-gateway/`)
- **Energy Optimization Service**: Battery scheduling algorithms (`microservices/energy-optimization-service/`)
- **Shared Libraries**: Common models and utilities (`shared/`)
- Service communication via HTTP and Redis message queue

## Common Commands

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run monolithic version locally
uvicorn main:app --reload

# Test microservices structure
python test_microservices.py
```

### Docker Operations
```bash
# Build and run monolithic version
docker-compose up --profile legacy

# Run microservices (default)
docker-compose up -d

# Start only infrastructure
docker-compose up -d postgres redis grafana

# View service logs
docker-compose logs -f api-gateway energy-optimization
```

### Testing
```bash
# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/optimize/1

# Test service health (microservices)
curl http://localhost:8000/api/services/health

# Check database connection
docker exec -it energy_postgres psql -U user -d energydb
```

### Database Operations
```bash
# Initialize tables (monolithic)
python -c "from utils.db import create_tables; create_tables()"

# Add sample IoT data
python -c "from utils.db import insert_sample_iot_data; insert_sample_iot_data()"
```

## High-Level Architecture

### Data Flow
1. **Data Ingestion**: ETL processes collect meter readings, weather forecasts, and IoT sensor data
2. **Storage**: PostgreSQL with TimescaleDB extension for time-series optimization
3. **Optimization**: Energy scheduling algorithms determine battery charge/discharge cycles
4. **Visualization**: Grafana dashboards display consumption, PV forecasts, and battery schedules

### Key Components

**Optimization Engine** (`optimization/scheduler.py` or `microservices/energy-optimization-service/optimization_engine.py`):
- Battery capacity management (default 10kWh)
- Charge/discharge scheduling based on consumption patterns
- Simple strategy: charge during low consumption (<1.5kW), discharge during high consumption (>2.5kW)

**Database Schema**:
- `meter_readings`: Household consumption data
- `pv_forecasts`: Solar panel output predictions  
- `weather_forecasts`: Temperature and irradiation data
- `iot_data`: IoT sensor readings with TimescaleDB hypertables

**ETL Processes**:
- `etl/streaming.py`: Simulates real-time meter readings (5-second intervals)
- `etl/batch.py`: Generates PV forecasts (10-second intervals)
- Both insert dummy data for demonstration

### Service Communication (Microservices)
- **HTTP**: Synchronous service-to-service calls via `shared/utils/http_client.py`
- **Redis**: Asynchronous messaging (infrastructure ready)
- **Service Registry**: Centralized service discovery in `ServiceRegistry` class

## Development Notes

### Adding New Microservices
1. Create service directory in `microservices/`
2. Follow pattern: `main.py`, `requirements.txt`, `Dockerfile`
3. Add service to `docker-compose.yml` 
4. Register in `shared/utils/http_client.py`
5. Update `MICROSERVICES_SETUP.md`

### Database Best Practices
- Use `shared/utils/database.py` for service-specific database connections
- Always use `text()` wrapper for raw SQL queries with SQLAlchemy 2.0
- Consider TimescaleDB hypertables for time-series data

### Migration Strategy
The system is designed for gradual migration from monolithic to microservices:
- Phase 1: Optimization Service (✅ Complete)
- Phase 2: Data Ingestion Service (Next)  
- Phase 3: Weather/PV, IoT, Household Services
- Phase 4: Database separation per service

### Testing Approach
- `test_microservices.py`: Validates service structure and shared library imports
- Health checks at `/health` endpoint for each service
- Service discovery testing via API Gateway

## Important Implementation Details

- **Battery Efficiency**: 95% charge/discharge efficiency built into optimization algorithms
- **Time Intervals**: System designed for 15-minute optimization intervals
- **Service Ports**: API Gateway on 8000, individual services use internal Docker networking
- **Backward Compatibility**: All original API endpoints maintained in API Gateway