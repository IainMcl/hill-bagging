import logging

# from src.users.dtos import LatLon, UserTotalWalkTravel, UserWalkTimes
from src.maps.dtos import MapsResponseDTO
from src.users.data import UserData
from src.users.dtos import LatLon, UserWalkTravelInfo

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

    @staticmethod
    def calculate_user_total_times(user_id: int) -> list[UserWalkTravelInfo]:
        """
        Calculate the total time for each walk for a user by summing the
        walk duration with twice the travel time (their and back).
        """
        walk_travel_infos = UserData.get_user_walks_travel_info(user_id)
        for walk in walk_travel_infos:
            total_time = (
                walk.walk_info.walk_duration_seconds
                + 2 * walk.travel_info.duration_seconds
            )
            walk.total_time_seconds = total_time
        return walk_travel_infos

    @staticmethod
    def display_user_walk_travel_info(
        walk_travel_infos: list[UserWalkTravelInfo],
    ) -> None:
        """
        Display the user's walk and travel information in a user-friendly format.
        """
        for walk in walk_travel_infos:
            print("==================================================")
            print(f"Walk Name: {walk.walk_info.walk_name}")
            print(f"URL: {walk.walk_info.walk_url}")
            print(f"Start Location: {walk.walk_info.walk_start_location}")
            print(f"Distance: {walk.walk_info.walk_distance_meters / 1000:.2f} km")
            print(f"Ascent: {walk.walk_info.walk_ascent_meters} m")
            print(
                "Duration: "
                f"{walk.walk_info.walk_duration_seconds // 3600}h "
                f"{(walk.walk_info.walk_duration_seconds % 3600) // 60}m"
            )
            print(f"Number of Hills: {walk.walk_info.number_of_hills}")
            print(f"Hills: {', '.join(walk.walk_info.hills)}")
            print("--------------------------------------------------")
            print("Travel Information:")
            print(
                f"  Travel Time: {walk.travel_info.duration_seconds // 3600}h "
                f"{(walk.travel_info.duration_seconds % 3600) // 60}m"
            )
            print(
                f"  Travel Distance: {walk.travel_info.distance_meters / 1000:.2f} km"
            )
            print("--------------------------------------------------")
            print("Total Trip Information:")
            if walk.total_time_seconds is not None:
                print(
                    f"  Total Time: {walk.total_time_seconds // 3600}h "
                    f"{(walk.total_time_seconds % 3600) // 60}m"
                )
            print("==================================================")
