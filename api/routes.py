from fastapi import APIRouter
from utils.db import get_session
from optimization.scheduler import optimize_energy
from sqlalchemy import text

router = APIRouter()


@router.get("/api/optimize/{household_id}")
def optimize(household_id: int):
    try:
        with get_session() as session:
            result = session.execute(
                text(
                    "SELECT * FROM meter_readings WHERE household_id = :hid ORDER BY timestamp DESC LIMIT 5"
                ),
                {"hid": household_id},
            )
            household_data = [dict(row._mapping) for row in result.fetchall()]

        if not household_data:
            return {"schedule": [], "message": "No data yet for this household"}

        schedule = optimize_energy(household_data)
        return {"schedule": schedule}

    except Exception as e:
        return {"error": str(e)}
