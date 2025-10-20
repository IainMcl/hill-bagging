import logging

logger = logging.getLogger(__name__)


class UsersService:
    @staticmethod
    def check_location(location: str) -> bool:
        """
        Check if the provided location is valid.
        The location should be given as a lat lon pair separated by a comma.
        e.g. "56.4907,-4.2026"
        """
        try:
            lat_str, lon_str = location.split(",")
            lat = float(lat_str)
            lon = float(lon_str)
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return True
            else:
                logger.debug(f"Location out of bounds: {location}")
                return False
        except ValueError:
            logger.debug(f"Invalid location format: {location}")
            return False
