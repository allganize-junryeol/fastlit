from pydantic import BaseModel


class Statistics(BaseModel):
    number_of_system: int
    number_of_hardware: int
    number_of_software: int
    updated_last_month: int
