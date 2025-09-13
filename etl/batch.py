import time
from utils.db import get_session
from sqlalchemy import text


def start_scheduler():
    print("Batch ETL started")
    while True:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        pv_output = 0.5  # dummy value
        data = {"timestamp": timestamp, "pv_output": pv_output}
        with get_session() as session:
            session.execute(
                text(
                    "INSERT INTO pv_forecasts (timestamp, pv_output) VALUES (:timestamp, :pv_output)"
                ),
                data,
            )
        print(f"Inserted PV forecast: {data}")
        time.sleep(10)
