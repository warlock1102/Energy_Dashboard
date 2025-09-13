# Hybrid ETL Implementation Guide — Smart-Home Energy Information System

**Purpose:** step-by-step lab-ready guide to implement a hybrid ETL (batch + streaming) pipeline for a Smart-Home / Residential Energy IS. Each step includes *what to do*, *commands/code snippets*, and *why it matters (significance)*.

---

## Scope & assumptions

* Lab-scale deployment (single server / small cluster). Moderate ingest (tens to low hundreds of messages/sec). If you expect thousands+/sec you'll want to move to Kafka+connectors.
* Time resolution: typical choices are 1 min / 5 min / 15 min depending on use-case; this guide uses 15-min aggregation as default but shows how to change it.
* Storage recommendation: **TimescaleDB (Postgres + hypertables)** for unified time-series + relational queries. Optionally: InfluxDB + PostgreSQL split.
* Languages/tools used: Python 3.10+, Docker Compose, paho-mqtt, SQLAlchemy, pandas, FastAPI, PuLP, Grafana.

---

## Quick architecture (text diagram)

```
Sensors / Simulators ---> MQTT Broker ---> Streaming Consumer (Python) ---> TimescaleDB (hypertable)
                           ^                                      ^
                           |                                      |
Batch Jobs (weather/tariff) --writes--> TimescaleDB   <--- Optimization worker / API ---> Smart Home Controller (MQTT/HTTP)
                                                           |
                                                       Dashboard (Grafana) / Streamlit (optional)
```

---

## 0. Prerequisites (what to install)

* Docker & Docker Compose
* Python 3.10+ and virtualenv
* psql client (optional)
* Editor + Git

**Significance:** ensures reproducible environment, easy cleanup, and portability.

---

## 1. Project planning & definitions

**What to do**

* Define objectives (demo vs research vs live control).
* Choose time resolution (e.g., 1 min / 15 min / hourly).
* List data sources & schemas: telemetry (meter), pv generation, battery state, tariffs, weather forecasts, household metadata.
* Define optimization metrics (cost minimization, autarky, revenue maximization) and priorities/weights.

**Significance**

* Clarifies scope and avoids premature technical choices. Data model and optimization objectives drive schema and pipeline cadence.

---

## 2. Choose storage & design schema

**Choice (lab recommendation):** TimescaleDB.

**Docker compose snippet (minimal):**

```yaml
version: "3.8"
services:
  timescaledb:
    image: timescale/timescaledb:latest
    environment:
      POSTGRES_PASSWORD: example
      POSTGRES_USER: demo
      POSTGRES_DB: energy
    ports: ["5432:5432"]
    volumes: ["ts_data:/var/lib/postgresql/data"]

  grafana:
    image: grafana/grafana:latest
    ports: ["3000:3000"]
    depends_on: ["timescaledb"]

  mosquitto:
    image: eclipse-mosquitto:latest
    ports: ["1883:1883"]
    volumes: ["./mosquitto/config:/mosquitto/config"]

volumes:
  ts_data:
```

**Significance**

* TimescaleDB provides hypertables and SQL support making joins across metadata and time-series easy. Grafana can connect directly.

---

## 3. Create DB schema & hypertables

**SQL examples (psql):**

```sql
-- connect to energy DB
-- households: static metadata
CREATE TABLE households (
  household_id   INT PRIMARY KEY,
  name           TEXT,
  location       TEXT,
  pv_capacity_kw DOUBLE PRECISION,
  battery_kwh    DOUBLE PRECISION
);

-- telemetry hypertable
CREATE TABLE meter_readings (
  household_id   INT NOT NULL,
  ts             TIMESTAMPTZ NOT NULL,
  consumption_w  DOUBLE PRECISION NOT NULL,
  PRIMARY KEY (household_id, ts)
);
SELECT create_hypertable('meter_readings','ts', chunk_time_interval => INTERVAL '1 day');

-- PV generation
CREATE TABLE pv_generation (
  household_id INT NOT NULL,
  ts           TIMESTAMPTZ NOT NULL,
  pv_w         DOUBLE PRECISION NOT NULL,
  PRIMARY KEY (household_id, ts)
);
SELECT create_hypertable('pv_generation','ts');

-- forecasts & tariffs (example)
CREATE TABLE weather_forecast (
  ts TIMESTAMPTZ NOT NULL,
  location TEXT,
  ghi DOUBLE PRECISION,
  PRIMARY KEY (location, ts)
);

CREATE TABLE tariffs (
  tariff_id SERIAL PRIMARY KEY,
  name TEXT,
  start_ts TIMESTAMPTZ,
  end_ts TIMESTAMPTZ,
  price_per_kwh DOUBLE PRECISION
);
```

**Significance**

* Explicit schema ensures reliable joins and constraints. Hypertables optimize large time-series writes/queries.

---

## 4. Streaming ingestion: MQTT -> Python consumer -> DB

**Producer:** sensors or simulator publish JSON to topics like `home/{id}/meter`.

**Consumer example (`streaming_consumer.py`):**

```python
import json
from sqlalchemy import create_engine, text
import paho.mqtt.client as mqtt

DB_URI = "postgresql+psycopg2://demo:example@timescaledb:5432/energy"
engine = create_engine(DB_URI, pool_pre_ping=True)

INSERT_SQL = text(
    """
    INSERT INTO meter_readings (household_id, ts, consumption_w)
    VALUES (:hid, :ts, :cons)
    ON CONFLICT (household_id, ts) DO UPDATE
    SET consumption_w = EXCLUDED.consumption_w
    """
)

buffer = []
BATCH_SIZE = 50

def flush_buffer():
    global buffer
    if not buffer:
        return
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO meter_readings (household_id, ts, consumption_w) VALUES (:hid,:ts,:cons)"), buffer)
    buffer = []

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload)
    # payload: {"household_id":1, "ts":"2025-09-12T10:00:00Z", "consumption_w":450}
    buffer.append({"hid": payload["household_id"], "ts": payload["ts"], "cons": payload["consumption_w"]})
    if len(buffer) >= BATCH_SIZE:
        flush_buffer()

client = mqtt.Client()
client.on_message = on_message
client.connect("mosquitto", 1883)
client.subscribe("home/+/meter")
client.loop_start()

# make sure a periodic flush runs (or flush on shutdown)

```

**Implementation notes**

* Batch inserts reduce DB overhead. Use COPY or multi-row insert for even higher throughput.
* For reliability, persist messages to a local queue (disk-backed) if DB is unavailable.

**Significance**

* Decouples sensors from DB. Batching improves throughput and stability.

---

## 5. Batch ingestion: scheduled jobs (weather / tariffs / forecasts)

**Scheduler options:** cron, APScheduler (Python), or Airflow for complex DAGs.

**APScheduler example:**

```python
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from sqlalchemy import create_engine, text

engine = create_engine("postgresql+psycopg2://demo:example@timescaledb:5432/energy")

def fetch_weather_and_store():
    # call a weather API (Open-Meteo / OpenWeather) and write rows to weather_forecast
    # parse response and insert into weather_forecast table
    pass

sched = BackgroundScheduler()
sched.add_job(fetch_weather_and_store, 'interval', hours=1)
sched.start()

# keep process alive or run under a process manager
```

**Significance**

* Fetching forecasts & tariffs on a schedule ensures the optimizer has current inputs for horizon planning.

---

## 6. Feature engineering & aggregation (pandas)

**Common transforms**

* Resample raw telemetry to optimizer resolution (e.g., 15-min)
* Compute rolling averages, peak demand, daily sums
* Align PV forecast, weather, price time series into a single feature table per household

**Example:**

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://demo:example@timescaledb:5432/energy")

sql = "SELECT * FROM meter_readings WHERE ts >= now()-interval '1 day'"
df = pd.read_sql(sql, engine, parse_dates=['ts'])

df = df.set_index('ts').groupby('household_id').resample('15T').mean().reset_index()
```

**Significance**

* The optimizer expects well-formed input at a fixed cadence. Feature engineering reduces noise and produces useful predictors.

---

## 7. API & orchestration (FastAPI)

**Endpoints to provide:**

* `/api/latest/{household_id}` — fetch aggregated time-series
* `/api/optimize` — trigger optimization with scenario payload
* `/api/schedule/{id}` — query last generated schedule

**FastAPI skeleton:**

```python
from fastapi import FastAPI
app = FastAPI()

@app.get('/api/latest/{hid}')
def latest(hid:int):
    # query aggregated table and return JSON
    return {}

@app.post('/api/optimize')
def optimize(payload: dict):
    # enqueue/trigger optimization worker
    return {'status': 'ok'}
```

**Significance**

* Clean separation between UI/dashboard and backend logic. Enables remote triggers and integration with automation.

---

## 8. Optimization worker (PuLP / Pyomo)

**Problem framing**

* Time discretization: t=0..T-1 (e.g., 96 slots for 24h\@15min)
* Variables: grid\_import\[t] (kW), battery\_charge\[t], battery\_discharge\[t], soc\[t], appliance\_on\[t] (binary)
* Constraints: battery SoC balance, SoC bounds, charge/discharge rates, appliance runtime windows, power flow balance
* Objective: weighted sum (cost, autarky, revenue)

**Example skeleton (PuLP):**

```python
import pulp

T = 96
prob = pulp.LpProblem('energy_opt', pulp.LpMinimize)

grid_import = pulp.LpVariable.dicts('grid_import', range(T), lowBound=0)
# add variables for battery charge/discharge, soc, etc.

# add constraints
# battery SoC dynamics: soc[t+1] = soc[t] + charge_eff*charge[t] - discharge[t]/discharge_eff

# objective: minimize sum(price[t]*grid_import[t]*dt - sell_price[t]*export[t]*dt)

prob.solve()

# extract solution and write schedule back to DB / push to controller
```

**Significance**

* The optimization produces actionable schedules for appliances & battery; selecting solver and problem form (LP vs MILP) impacts runtime.

---

## 9. Smart Home Controller (actuation)

**Options:**

* Publish schedules/commands to MQTT topics (e.g., `home/{id}/cmd`) that smart appliances subscribe to
* Use HTTP callbacks if appliances support it

**Recommended pattern:**

* Optimizer writes schedule into a `schedules` DB table. A small controller/bridge process reads schedules and publishes MQTT commands at the correct time.

**Significance**

* Keeps the optimizer stateless; controller handles reliability and retries. Using MQTT decouples components.

---

## 10. Dashboarding & visualization

**Grafana**

* Add TimescaleDB as PostgreSQL datasource (host, port, db, user, password)
* Build panels: consumption, PV generation, SOC, price vs grid-import
* Use annotations/alerts for missing telemetry or SoC limits

**Streamlit (optional)**

* For scenario definition and interactive runs (POST to `/api/optimize`)

**Significance**

* Grafana is excellent at live time-series monitoring, while Streamlit is better for interactive scenario configuration and demonstration.

---

## 11. Testing & verification

**Unit tests**

* Transform functions (pandas resampling), API endpoints, optimizer constraints

**Integration tests**

* Use docker-compose test stack: run simulator sending MQTT messages → assert rows in DB → trigger optimize → assert schedule created

**Scenario-based tests**

* Baseline vs optimized: compute metrics (cost, autarky) and store results for regression testing

**Significance**

* Automated tests provide objective verification required by the project brief.

---

## 12. Observability, logging & security

* Centralize logs (files/Fluentd) and expose metrics (Prometheus + Grafana if needed)
* Secure MQTT (TLS + client auth) and FastAPI (HTTPS + tokens)
* Use environment variables or Docker secrets for credentials
* Backup DB and retention policies; enable TimescaleDB compression for older chunks

**Significance**

* Production-safe practices even in lab ensure realistic demos and prevent leaks or data loss.

---

## 13. CI/CD and reproducibility

**CI pipeline tasks**

* Linting & unit tests
* Docker compose up (test stack) + integration tests that simulate mqtt
* Build release artifacts

**Significance**

* Ensures reproducible demos and easier collaboration.

---

## 14. Scaling & optional upgrades

* **High throughput:** move streaming to Kafka + Kafka Connect + Kafka Streams / Flink
* **Complex DAGs:** use Airflow for batch orchestration
* **Compute heavy optimization:** containerize & scale with Kubernetes / job queue (RabbitMQ/Celery)
* **Storage:** read replicas, compression policies, retention, partitioning

**Significance**

* Gives a clear migration path from lab to pilot and production.

---

## 15. Quick start checklist (first runs)

1. `git init` + create repo
2. `docker compose up -d` (TimescaleDB, Grafana, Mosquitto)
3. Connect psql and create DB schema
4. Start streaming consumer and a small local simulator publisher
5. Verify telemetry reaches DB and visualize in Grafana
6. Add APScheduler batch job to fetch forecast
7. Implement and run a simple PuLP optimization with the last 24h data
8. Implement FastAPI endpoints and link Streamlit UI to call optimize
9. Run integration tests

**Significance**

* A lean path to a working demo in your lab within a few hours.

---

## Appendix: Useful commands & snippets

**psql connect (local):**

```
psql -h localhost -U demo -d energy
```

**Bring up stack:**

```
docker compose up -d
```

**Install Python deps:**

```
python -m venv .venv
source .venv/bin/activate
pip install paho-mqtt sqlalchemy psycopg2-binary apscheduler fastapi uvicorn pandas pulp
```

**Run FastAPI dev server:**

```
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Closing notes & next steps

* If you want, I can generate a minimal GitHub-ready repo scaffold with:

  * `docker-compose.yml`
  * DB schema SQL
  * streaming consumer
  * batch job
  * simple FastAPI app
  * example optimizer (PuLP)

* I assumed a lab-scale workload; if you provide estimated message rates, number of households and retention, I can tune chunk intervals and DB settings for performance.

---

*End of guide.*

