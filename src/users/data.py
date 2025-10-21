from src.database.api import DatabaseAPI
import logging
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
        except Exception:
            logger.exception(f"An error occurred while saving user data for {name}")

    @staticmethod
    def fetch_user_location(name: str) -> LatLon | None:
        """Fetch the location of a user from the database."""
        db_api = DatabaseAPI()
        try:
            with db_api.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT location FROM users WHERE name = ?
                    """,
                    (name,),
                )
                result = cursor.fetchone()
                return UserData._parse_lat_lon_string(result[0]) if result else None
        except Exception:
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
