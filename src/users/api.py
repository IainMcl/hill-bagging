import logging

from walkhighlands.api import WalkhighlandsAPI
from src.users.data import UserData
from src.users.service import UsersService
from src.users.location_service import get_lat_lon_from_postcode
from src.users.dtos import LatLon
from src.maps.api import MapsApi

logger = logging.getLogger(__name__)


class UsersAPI:
    @staticmethod
    def initialize_users():
        logger.info("Initializing users...")
        UserData.create_user_table()
        UserData.create_user_walk_directions_table()
        logger.info("Initialization complete.")

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
    def get_user_location(name: str) -> LatLon:
        _, location = UserData.fetch_user_location(name) or (None, None)
        if location is None:
            logger.warning(f"User not found: {name}")
            raise ValueError("User not found")
        return location

    @staticmethod
    def get_walk_directions_for_user(user: str) -> None:
        """
        For the user get and store the time and distance between the users
        location and each of the walk starting points.
        """
        user_id, user_location = UserData.fetch_user_location(user) or (None, None)
        if user_location is None or user_id is None:
            logger.error("User location not found", extra={"user": user})
            raise ValueError("User not found")
        user_location_string = UsersAPI._parse_lat_lon_to_string(user_location)
        walk_starting_locations = WalkhighlandsAPI.get_walk_start_locations()
        logger.debug(
            "Fetched walk starting locations",
            extra={
                "starting_locations_count": len(walk_starting_locations),
                "user": user,
            },
        )
        for walk in walk_starting_locations:
            try:
                map_response = MapsApi.get_driving_distance_and_time(
                    origin=user_location_string, destination=walk.walk_start_location
                )
                UsersService.save_walk_directions_for_user(
                    user_id, walk.walk_id, map_response
                )
                logger.info("Breaking after 1 for testing")
                break
            except Exception as e:
                logger.error(
                    "Error fetching and saving directions for user",
                    extra={"user": user, "walk_id": walk.walk_id, "error": str(e)},
                )

    @staticmethod
    def _parse_lat_lon_to_string(location: LatLon) -> str:
        return f"{location.lat},{location.lon}"
