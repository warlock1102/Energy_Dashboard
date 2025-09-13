from fastapi import FastAPI
from api.routes import router
import threading
from etl import streaming, batch
from utils.db import create_tables

app = FastAPI()
app.include_router(router)

# Create tables at startup
create_tables()

# Start ETL modules in background threads
threading.Thread(target=streaming.start_stream, daemon=True).start()
threading.Thread(target=batch.start_scheduler, daemon=True).start()


@app.get("/")
def root():
    return {"message": "Energy IS running!"}
