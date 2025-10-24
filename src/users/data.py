from src.database.api import DatabaseAPI
import sqlite3
import logging
from src.maps.dtos import MapsResponseDTO
from src.users.dtos import LatLon, TravelInfo, UserWalkTravelInfo, WalkInfo
from src.utils.distance import kilometers_to_meters
from src.utils.time import hours_to_seconds

logger = logging.getLogger(__name__)


class UserData:
    @staticmethod
    def create_user_table() -> None:
        """Create the users table in the database if it doesn't exist."""
        db_api = DatabaseAPI()
        with db_api.db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    location TEXT NOT NULL
                )
                """
            )
            conn.commit()

    @staticmethod
    def create_user_walk_directions_table() -> None:
        """Create the user_walk_directions table in the database if it doesn't exist."""
        db_api = DatabaseAPI()
        with db_api.db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_walk_directions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    walk_id INTEGER NOT NULL,
                    distance INTEGER,
                    duration INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (walk_id) REFERENCES walks(id),
                    UNIQUE(user_id, walk_id)
                )
                """
            )
            conn.commit()

    @staticmethod
    def save_user_data(name: str, location: LatLon) -> None:
        """Save user data to the database."""
        db_api = DatabaseAPI()
        location_str = UserData._get_lat_lon_string(location)
        try:
            with db_api.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO users (name, location)
                    VALUES (?, ?)
                    """,
                    (name, location_str),
                )
                conn.commit()
        except sqlite3.DatabaseError:
            logger.exception(f"An error occurred while saving user data for {name}")

    @staticmethod
    def fetch_user_location(name: str) -> tuple[int, LatLon] | None:
        """Fetch the location of a user from the database."""
        db_api = DatabaseAPI()
        try:
            with db_api.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, location FROM users WHERE name = ?
                    """,
                    (name,),
                )
                result = cursor.fetchone()
                return (
                    (result[0], UserData._parse_lat_lon_string(result[1]))
                    if result
                    else None
                )
        except sqlite3.Error:
            logger.exception(f"An error occurred while fetching location for {name}")
            return None

    @staticmethod
    def _get_lat_lon_string(location: LatLon) -> str:
        """Convert LatLon object to a string representation."""
        return f"{location.lat},{location.lon}"

    @staticmethod
    def _parse_lat_lon_string(location_str: str) -> LatLon:
        """Parse a string representation of LatLon back into a LatLon object."""
        latitude, longitude = map(float, location_str.split(","))
        return LatLon(lat=latitude, lon=longitude)

    @staticmethod
    def save_walk_directions(
        user_id: int, walk_id: int, map_response: MapsResponseDTO
    ) -> None:
        """
        Save the walking directions for a user to a specific walk.
        """
        logger.debug(
            "Saving walk directions", extra={"user_id": user_id, "walk_id": walk_id}
        )
        db_api = DatabaseAPI()
        try:
            with db_api.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO user_walk_directions (user_id, walk_id, distance, duration)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        walk_id,
                        map_response.distance_meters,
                        map_response.duration_seconds,
                    ),
                )
                conn.commit()
                logger.debug("Walk directions saved successfully")
        except sqlite3.IntegrityError:
            logger.warning(
                "Directions for this user and walk already exist.",
                extra={"user_id": user_id, "walk_id": walk_id},
            )
        except sqlite3.DatabaseError:
            logger.exception(
                "An error occurred while saving walk directions",
                extra={"user_id": user_id, "walk_id": walk_id},
            )

    @staticmethod
    def check_walk_directions_exist(user_id: int, walk_id: int) -> bool:
        """Check if walk directions already exist for a user and walk."""
        db_api = DatabaseAPI()
        try:
            with db_api.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT 1 FROM user_walk_directions
                    WHERE user_id = ? AND walk_id = ?
                    """,
                    (user_id, walk_id),
                )
                result = cursor.fetchone()
                return result is not None
        except sqlite3.Error:
            logger.exception(
                "An error occurred while checking walk directions",
                extra={"user_id": user_id, "walk_id": walk_id},
            )
            return False

    @staticmethod
    def get_user_id_for_name(user_name: str) -> int | None:
        """Get the user ID for a given user name."""
        db_api = DatabaseAPI()
        try:
            with db_api.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id FROM users WHERE name = ?
                    """,
                    (user_name,),
                )
                result = cursor.fetchone()
                return result[0] if result else None
        except sqlite3.Error:
            logger.exception(
                "An error occurred while fetching user ID",
                extra={"user_name": user_name},
            )
            return None

    @staticmethod
    def get_user_walks_travel_info(user_id: int) -> list[UserWalkTravelInfo]:
        """
        Get the information for all user walks including walk details and travel info.
        """
        db_api = DatabaseAPI()
        try:
            with db_api.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT
                        w.id as walk_id,
                        w.title as walk_title,
                        w.start_location as walk_start_location,
                        w.ascent as walk_ascent_meters,
                        w.distance as walk_distance_km,
                        w.time as walk_duration_hours,
                        w.url as walk_url,
                        uwd.distance as travel_distance_meters,
                        uwd.duration as travel_duration_seconds,
                        GROUP_CONCAT(h.name) as hill_names
                    FROM
                        user_walk_directions uwd
                    JOIN
                        walks w ON uwd.walk_id = w.id
                    LEFT JOIN
                        walk_hill_decomposition whd ON w.id = whd.walk_id
                    LEFT JOIN
                        hills h ON whd.hill_id = h.id
                    WHERE
                        uwd.user_id = ?
                    GROUP BY
                        w.id
                    ORDER BY
                        w.id
                    """,
                    (user_id,),
                )
                results = cursor.fetchall()

                user_walks_info = []
                for row in results:
                    (
                        walk_id,
                        walk_title,
                        walk_start_location,
                        walk_ascent_meters,
                        walk_distance_km,
                        walk_duration_hours,
                        walk_url,
                        travel_distance_meters,
                        travel_duration_seconds,
                        hill_names,
                    ) = row
                    hills = hill_names.split(",") if hill_names else []
                    walk_info = WalkInfo(
                        walk_id=walk_id,
                        walk_name=walk_title,
                        walk_start_location=walk_start_location,
                        walk_ascent_meters=walk_ascent_meters,
                        walk_distance_meters=kilometers_to_meters(walk_distance_km),
                        walk_duration_seconds=hours_to_seconds(
                            float(walk_duration_hours)
                        ),
                        walk_url=walk_url,
                        number_of_hills=len(hills),
                        hills=hills,
                    )
                    travel_info = TravelInfo(
                        distance_meters=travel_distance_meters,
                        duration_seconds=travel_duration_seconds,
                    )
                    user_walks_info.append(
                        UserWalkTravelInfo(
                            user_id=user_id,
                            walk_info=walk_info,
                            travel_info=travel_info,
                        )
                    )
                return user_walks_info

        except sqlite3.Error:
            logger.exception(
                "An error occurred while fetching user walks travel info",
                extra={"user_id": user_id},
            )
            return []
