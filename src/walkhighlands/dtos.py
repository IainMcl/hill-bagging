from pydantic import BaseModel


class HillPageData(BaseModel):
    name: str
    url: str
    region: str
    altitude: int


class WalkData(BaseModel):
    title: str
    url: str
    distance_km: float
    ascent_m: int
    duration_hr: float
    bog_factor: int
    user_rating: float
    start_grid_ref: str
    grade: int
    start_location: str
    hill_ids: list[int]


class Walk(BaseModel):
    title: str
    url: str


class WalkStartLocationDTO(BaseModel):
    walk_id: int
    walk_start_location: str
