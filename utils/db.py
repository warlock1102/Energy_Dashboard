from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import contextlib

DATABASE_URL = "postgresql+psycopg2://user:password@postgres:5432/energydb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


@contextlib.contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def create_tables():
    with get_session() as session:
        session.execute(
            text("""
        CREATE TABLE IF NOT EXISTS meter_readings (
            household_id INT,
            timestamp TIMESTAMP,
            consumption FLOAT
        );
        """)
        )
        session.execute(
            text("""
        CREATE TABLE IF NOT EXISTS pv_forecasts (
            timestamp TIMESTAMP,
            pv_output FLOAT
        );
        """)
        )
        session.execute(
            text("""
        CREATE TABLE IF NOT EXISTS weather_forecasts (
            timestamp TIMESTAMP,
            temperature FLOAT,
            irradiation FLOAT
        );
        """)
        )
