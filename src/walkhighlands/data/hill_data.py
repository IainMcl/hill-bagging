from src.database.api import DatabaseAPI
from src.walkhighlands.dtos import HillPageData
import logging

logger = logging.getLogger(__name__)


class WalkhighlandsData:
    @staticmethod
    def create_hill_data_table() -> None:
        """Create the hills table in the database if it doesn't exist."""
        logger.info("Creating hills table in the database if it doesn't exist.")
        db_api = DatabaseAPI()
        with db_api.db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS hills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    region TEXT NOT NULL,
                    altitude INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    @staticmethod
    def save_hill_data(hill_data: HillPageData) -> None:
        """Save hill data to the database."""
        db_api = DatabaseAPI()
        try:
            with db_api.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO hills (url, name, region, altitude)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        hill_data.url,
                        hill_data.name,
                        hill_data.region,
                        hill_data.altitude,
                    ),
                )
                conn.commit()
            logger.info(f"Saved hill data for {hill_data.name} to the database.")
        except Exception:
            logger.exception(f"An error occurred while saving hill data")
