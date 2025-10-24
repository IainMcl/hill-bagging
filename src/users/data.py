from src.database.api import DatabaseAPI
import sqlite3
import logging
from src.maps.dtos import MapsResponseDTO
from src.users.dtos import LatLon

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
