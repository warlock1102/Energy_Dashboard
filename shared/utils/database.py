from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import contextlib
import os


def get_database_url(service_name: str = "main") -> str:
    """Get database URL for a specific service"""
    if service_name == "main":
        # Main database for backward compatibility
        return os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@postgres:5432/energydb")
    else:
        # Service-specific databases (future implementation)
        db_name = f"energydb_{service_name}"
        return f"postgresql+psycopg2://user:password@postgres:5432/{db_name}"


def create_engine_for_service(service_name: str = "main"):
    """Create SQLAlchemy engine for a specific service"""
    database_url = get_database_url(service_name)
    return create_engine(database_url)


@contextlib.contextmanager
def get_session(service_name: str = "main"):
    """Get database session for a specific service"""
    engine = create_engine_for_service(service_name)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def create_tables_for_service(service_name: str = "main"):
    """Create tables for a specific service"""
    with get_session(service_name) as session:
        if service_name in ["main", "household"]:
            session.execute(
                text("""
            CREATE TABLE IF NOT EXISTS meter_readings (
                household_id INT,
                timestamp TIMESTAMP,
                consumption FLOAT
            );
            """)
            )

        if service_name in ["main", "weather-pv"]:
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

        if service_name in ["main", "iot"]:
            session.execute(
                text("""
            CREATE TABLE IF NOT EXISTS iot_data (
                time TIMESTAMP NOT NULL,
                temperature FLOAT,
                humidity FLOAT,
                energy_kwh FLOAT,
                room VARCHAR(50),
                device_id VARCHAR(100)
            );
            """)
            )