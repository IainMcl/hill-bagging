import logging
from src.users.dtos import LatLon

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
