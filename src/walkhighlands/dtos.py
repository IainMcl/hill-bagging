from pydantic import BaseModel


class HillPageData(BaseModel):
    name: str
    url: str
    region: str
    altitude: int
