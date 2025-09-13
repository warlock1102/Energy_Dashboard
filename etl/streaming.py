import time
from utils.db import get_session
from sqlalchemy import text


def start_stream():
    print("Streaming ETL started")
    household_id = 1
    while True:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        consumption = 1.0  # dummy value
        data = {
            "household_id": household_id,
            "timestamp": timestamp,
            "consumption": consumption,
        }
        with get_session() as session:
            session.execute(
                text(
                    "INSERT INTO meter_readings (household_id, timestamp, consumption) "
                    "VALUES (:household_id, :timestamp, :consumption)"
                ),
                data,
            )
        print(f"Inserted meter reading: {data}")
        time.sleep(5)
