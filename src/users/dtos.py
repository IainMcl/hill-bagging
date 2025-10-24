from pydantic import BaseModel


class LatLon(BaseModel):
    lat: float
    lon: float


class WalkInfo(BaseModel):
    walk_id: int
    walk_name: str
    walk_start_location: str
    walk_ascent_meters: int
    walk_distance_meters: int
    walk_duration_seconds: int
    walk_url: str
    number_of_hills: int
    hills: list[str]


class TravelInfo(BaseModel):
    distance_meters: int
    duration_seconds: int


class UserWalkTravelInfo(BaseModel):
    user_id: int
    walk_info: WalkInfo
    travel_info: TravelInfo
    total_time_seconds: int | None = None
