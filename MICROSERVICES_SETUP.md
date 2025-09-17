# Energy Dashboard - Microservices Architecture

This document describes the microservices conversion of the Energy Dashboard system.

## 🏗️ Architecture Overview

The system has been decomposed into the following microservices:

### Implemented Services

1. **API Gateway** (`microservices/api-gateway/`)
   - Central entry point for all client requests
   - Routes requests to appropriate microservices
   - Handles backward compatibility with original API
   - Port: 8000

2. **Energy Optimization Service** (`microservices/energy-optimization-service/`)
   - Handles household energy optimization algorithms
   - Battery charging/discharging scheduling
   - Enhanced optimization logic with battery state management
   - Port: Internal (accessed via API Gateway)

### Planned Services (Directories created, implementation pending)

3. **Data Ingestion Service** (`microservices/data-ingestion-service/`)
   - ETL batch and streaming operations
   - Handles meter readings and sensor data ingestion

4. **Household Service** (`microservices/household-service/`)
   - Manages household data and meter readings
   - Household-specific configurations

5. **Weather & PV Service** (`microservices/weather-pv-service/`)
   - Weather forecasts and PV generation data
   - Solar panel output predictions

6. **IoT Service** (`microservices/iot-service/`)
   - IoT sensor data processing
   - Device management
   - Time-series data optimization

### Infrastructure Services

- **PostgreSQL**: Primary database
- **Redis**: Message queue for inter-service communication
- **Grafana**: Visualization and monitoring

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed and running
- Docker Compose v2+

### 1. Start Infrastructure Services

```bash
# Start database, message queue, and Grafana
docker-compose up -d postgres redis grafana
```

### 2. Start Microservices

```bash
# Start API Gateway and Optimization Service
docker-compose up -d api-gateway energy-optimization
```

### 3. Test the Setup

```bash
# Test API Gateway health
curl http://localhost:8000/health

# Test service health
curl http://localhost:8000/api/services/health

# Test optimization (backward compatible)
curl http://localhost:8000/api/optimize/1
```

## 📁 Directory Structure

```
Dashboard/
├── microservices/
│   ├── api-gateway/
│   │   ├── main.py              # FastAPI gateway app
│   │   ├── requirements.txt     # Dependencies
│   │   └── Dockerfile          # Container definition
│   ├── energy-optimization-service/
│   │   ├── main.py              # Optimization service
│   │   ├── optimization_engine.py # Core optimization logic
│   │   ├── requirements.txt     # Dependencies
│   │   └── Dockerfile          # Container definition
│   └── [other services...]     # Future implementations
├── shared/
│   ├── models/
│   │   └── schemas.py          # Pydantic data models
│   └── utils/
│   │   ├── database.py         # Database utilities
│   │   └── http_client.py      # Inter-service communication
├── docker-compose.yml          # Multi-service orchestration
└── test_microservices.py       # Validation script
```

## 🔧 Development

### Testing the Setup

Run the validation script:

```bash
python test_microservices.py
```

### Running Individual Services Locally

```bash
# Install dependencies
cd microservices/energy-optimization-service
pip install -r requirements.txt

# Run service
uvicorn main:app --reload --port 8001
```

### Adding New Services

1. Create service directory in `microservices/`
2. Add `main.py`, `requirements.txt`, and `Dockerfile`
3. Update `docker-compose.yml` to include the new service
4. Register service in `shared/utils/http_client.py`

## 🔄 Migration Strategy

### Phase 1: Optimization Service (✅ Complete)
- Extracted energy optimization logic
- Created standalone FastAPI service
- Maintained backward compatibility

### Phase 2: Data Ingestion (Next)
- Move ETL processes to separate service
- Implement message queue patterns
- Update database write patterns

### Phase 3: Additional Services
- Extract Weather/PV service
- Extract IoT service
- Extract Household service

### Phase 4: Database Separation
- Consider separate databases per service
- Implement event sourcing patterns

## 🌐 API Changes

### Backward Compatible Endpoints

The API Gateway maintains all original endpoints:

- `GET /api/optimize/{household_id}` - Original optimization endpoint
- `GET /` - Service status

### New Endpoints

- `GET /health` - Service health check
- `POST /api/optimize` - Advanced optimization with full request model
- `GET /api/services/health` - Check health of all microservices

## 📊 Benefits Achieved

1. **Service Independence**: Optimization service can be scaled independently
2. **Technology Flexibility**: Each service can use different technologies
3. **Fault Isolation**: Service failures don't affect the entire system
4. **Deployment Flexibility**: Services can be deployed independently
5. **Development Team Scaling**: Different teams can work on different services

## 🔍 Monitoring and Debugging

### Service Logs

```bash
# View API Gateway logs
docker-compose logs -f api-gateway

# View Optimization Service logs
docker-compose logs -f energy-optimization

# View all service logs
docker-compose logs -f
```

### Health Checks

Each service provides:
- `GET /health` - Service health status
- `GET /` - Service information

### Service Communication

Services communicate via:
- **HTTP**: For synchronous operations
- **Redis**: For asynchronous messaging (ready for implementation)

## 🚧 Known Limitations

1. **Database Sharing**: All services currently share the main database
2. **Authentication**: Not yet implemented across services
3. **Circuit Breakers**: Not yet implemented for resilience
4. **Distributed Tracing**: Not yet implemented for debugging

## 📋 Next Steps

1. **Implement remaining services** (Data Ingestion, Household, Weather/PV, IoT)
2. **Add message queue patterns** for asynchronous communication
3. **Implement authentication/authorization** across services
4. **Add monitoring and metrics** (Prometheus, Grafana)
5. **Implement circuit breakers** for resilience
6. **Add distributed tracing** (Jaeger, Zipkin)
7. **Consider database per service** pattern

## 🤝 Contributing

When adding new microservices:

1. Follow the existing structure pattern
2. Use shared models and utilities from `shared/`
3. Add proper health checks
4. Update documentation
5. Add service to docker-compose.yml
6. Test inter-service communication