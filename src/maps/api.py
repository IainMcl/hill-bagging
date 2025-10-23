import logging

from src.maps.dtos import MapsResponseDTO
from src.maps.service import MapsService


logger = logging.getLogger(__name__)


class MapsApi:
    @staticmethod
    def get_driving_distance_and_time(origin: str, destination: str) -> MapsResponseDTO:
        """Get driving distance and time between two locations."""
        maps_service = MapsService()
        result = maps_service.get_directions(
            origin=origin, destination=destination, mode="driving"
        )
        if result is None:
            logger.error(
                "Failed to get driving directions",
                extra={"origin": origin, "destination": destination},
            )
            raise ValueError("Could not retrieve driving directions.")
        return result
