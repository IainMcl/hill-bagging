from src.database.api import DatabaseAPI
import logging

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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    location TEXT
                )
                """
            )
            conn.commit()

    @staticmethod
    def save_user_data(name: str, location: str) -> None:
        """Save user data to the database."""
        db_api = DatabaseAPI()
        try:
            with db_api.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO users (name, location)
                    VALUES (?, ?)
                    """,
                    (name, location),
                )
                conn.commit()
        except Exception:
            logger.exception(f"An error occurred while saving user data for {name}")
