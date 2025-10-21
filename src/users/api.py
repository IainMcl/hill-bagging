import logging
from src.users.data import UserData
from src.users.service import UsersService
from src.users.location_service import get_lat_lon_from_postcode

logger = logging.getLogger(__name__)


class UsersAPI:
    @staticmethod
    def initialize_users():
        logger.info("UsersAPI: Initializing users...")
        UserData.create_user_table()

    @staticmethod
    def add_user(name: str, postcode: str) -> None:
        try:
            location = get_lat_lon_from_postcode(postcode)
        except Exception as e:
            logger.error(
                "Error fetching location from postcode",
                extra={"postcode": postcode, "error": str(e)},
            )
            return
        if not UsersService.check_location(location):
            logger.error(
                "Invalid location provided",
                extra={"location": location, "postcode": postcode},
            )
            return

        UserData.save_user_data(name, location)

    @staticmethod
    def get_user_location(name: str) -> str:
        location = UserData.fetch_user_location(name)
        if location is None:
            logger.warning(f"User not found: {name}")
            raise ValueError("User not found")
        return location
