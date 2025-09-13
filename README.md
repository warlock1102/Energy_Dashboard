# Energy Dashboard Information System

This project implements an **Energy Information System (IS)** for households and residential areas.
It allows you to simulate and optimize energy demand, photovoltaic (PV) generation, battery storage, and flexible appliances.
The system provides a **FastAPI backend**, **PostgreSQL database**, and **Grafana dashboard** for visualization.

---

## Features

* Weather forecasts and PV generation data
* Household meter readings (simulated)
* Energy demand optimization
* Flexible and static tariffs
* Battery charging/discharging schedules
* Operational recommendations for smart home appliances
* Visualization via Grafana

---

## Prerequisites

* [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
* Optional: Python 3.11+ (for development/testing outside Docker)

---

## Project Structure

```
Dashboard/
├─ api/
│  └─ routes.py
├─ etl/
│  ├─ batch.py
│  └─ streaming.py
├─ utils/
│  └─ db.py
├─ main.py
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
└─ README.md
```

---

## Setup and Run (Docker)

1. **Clone the repository**

```bash
git clone <your-repo-url>
cd Dashboard
```

2. **Build and start the containers**

```bash
docker-compose up -d --build
```

3. **Check running containers**

```bash
docker ps
```

You should see:

* `energy_fastapi` → FastAPI backend on port 8000
* `energy_postgres` → PostgreSQL database on port 5432
* `energy_grafana` → Grafana dashboard on port 3000

4. **Check FastAPI logs**

```bash
docker logs -f energy_fastapi
```

---

## Accessing Services

* **FastAPI API**
  [http://localhost:8000](http://localhost:8000)
  Example endpoint to run optimization:

  ```bash
  curl http://localhost:8000/api/optimize/1
  ```

* **Grafana Dashboard**
  [http://localhost:3000](http://localhost:3000)
  Default login:

  * Username: `admin`
  * Password: `admin`
    Import the provided dashboard JSON or create new panels connected to the PostgreSQL datasource.

* **PostgreSQL Database**

```bash
docker exec -it energy_postgres psql -U energy_user -d energydb
```

---

## Running Locally (Optional)

1. **Create Python virtual environment**

```bash
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Run FastAPI**

```bash
uvicorn main:app --reload
```

---

## Development Notes

* The ETL process includes **batch and streaming** ingestion of energy data.
* PostgreSQL must be pre-configured with the `energy_user` and `energydb` database.
* FastAPI endpoints provide energy optimization and scenario simulation.
* Grafana panels are pre-configured to visualize:

  * Household energy consumption
  * PV forecast
  * Battery schedule

---

## Stopping and Cleaning

Stop all containers:

```bash
docker-compose down
```

Remove PostgreSQL persistent volume (resets database):

```bash
docker volume rm dashboard_pgdata
```

---

## Troubleshooting

* **PostgreSQL connection error**: Make sure the username and password in `docker-compose.yml` match your code.
* **Grafana shows no data**: Check that FastAPI is inserting data into the PostgreSQL tables (`meter_readings`, `pv_forecasts`).
* **Internal server errors**: Ensure `SQLAlchemy` queries use `text()` for raw SQL:

```python
from sqlalchemy import text
session.execute(text("SELECT * FROM meter_readings"))
```

---

## References

* [FastAPI Documentation](https://fastapi.tiangolo.com/)
* [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
* [Grafana Docker Image](https://hub.docker.com/r/grafana/grafana)
* [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
