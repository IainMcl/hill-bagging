import logging
from src.users.dtos import LatLon
from src.maps.dtos import MapsResponseDTO
from src.users.data import UserData

logger = logging.getLogger(__name__)


class UsersService:
    @staticmethod
    def check_location(location: LatLon) -> bool:
        """
        Check if the provided location is valid.
        """
        try:
            if -90 <= location.lat <= 90 and -180 <= location.lon <= 180:
                return True
            return False
        except ValueError:
            logger.debug(f"Invalid location format: {location}")
            return False

    @staticmethod
    def save_walk_directions_for_user(
        user_id: int, walk_id: int, map_response: MapsResponseDTO
    ) -> None:
        """
        Save the walking directions for a user to a specific walk.
        """
        UserData.save_walk_directions(user_id, walk_id, map_response)
