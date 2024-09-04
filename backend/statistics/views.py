

import random
from fastapi import APIRouter

from backend.statistics.models import Statistics


router = APIRouter()

@router.get("/statistics", response_model=Statistics)
async def get_statistics():
    return Statistics(
        number_of_system=random.randint(5, 10),
        number_of_hardware=random.randint(5, 10),
        number_of_software=random.randint(5, 10),
        updated_last_month=random.randint(5, 10),
    )