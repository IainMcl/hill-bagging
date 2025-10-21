from pydantic import BaseModel


class LatLon(BaseModel):
    lat: float
    lon: float
