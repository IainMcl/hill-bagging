from pydantic import BaseModel


class MapsResponseDTO(BaseModel):
    origin: str
    destination: str
    distance_meters: int
    duration_seconds: int
