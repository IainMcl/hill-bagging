from src.database.api import DatabaseAPI
from src.walkhighlands.dtos import HillPageData, WalkData
import logging
import sqlite3

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
        hill_data.url = WalkhighlandsData._sanitize_url(hill_data.url)
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

    @staticmethod
    def insert_walk(walk_data: WalkData) -> None:
        """Insert walk data into the database."""
        url = WalkhighlandsData._sanitize_url(walk_data.url)
        db_api = DatabaseAPI()
        try:
            with db_api.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO walks (title, url, grade, bog_factor, user_rating, distance, time, ascent, start_grid_ref, start_location)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        walk_data.title,
                        walk_data.url,
                        walk_data.grade,
                        walk_data.bog_factor,
                        walk_data.user_rating,
                        walk_data.distance_km,
                        walk_data.duration_hr,
                        walk_data.ascent_m,
                        walk_data.start_grid_ref,
                        walk_data.start_location,
                    ),
                )
                walk_id = cursor.lastrowid
                logger.info(f"Inserted walk with ID: {walk_id}")
                for hill_id in walk_data.hill_ids:
                    logger.info(f"Inserting into walk_hill_decomposition: hill_id={hill_id}, walk_id={walk_id}")
                    cursor.execute(
                        """
                        INSERT INTO walk_hill_decomposition (hill_id, walk_id)
                        VALUES (?, ?)
                        """,
                        (hill_id, walk_id),
                    )
                conn.commit()
            logger.info(f"Inserted walk data for {walk_data.title} into the database.")
        except sqlite3.IntegrityError:
            logger.warning(
                f"Walk with URL {walk_data.url} already exists in the database."
            )
        except Exception:
            logger.exception("An error occurred while inserting walk data")

    @staticmethod
    def create_walk_data_table() -> None:
        """Create the hill metadata table in the database if it doesn't exist."""
        logger.info("Creating hill metadata table in the database if it doesn't exist.")
        db_api = DatabaseAPI()
        with db_api.db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS walks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    grade INTEGER NOT NULL,
                    bog_factor INTEGER NOT NULL,
                    user_rating REAL NOT NULL,
                    distance REAL NOT NULL,
                    time TEXT NOT NULL,
                    ascent INTEGER NOT NULL,
                    start_grid_ref TEXT NOT NULL,
                    start_location TEXT
                )
                """
            )
            conn.commit()

    @staticmethod
    def create_walk_hill_decomp_table() -> None:
        """Create the walk hill decomposition table in the database if it doesn't exist."""
        logger.info(
            "Creating walk hill decomposition table in the database if it doesn't exist."
        )
        db_api = DatabaseAPI()
        with db_api.db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS walk_hill_decomposition (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hill_id INTEGER NOT NULL,
                    walk_id INTEGER NOT NULL,
                    FOREIGN KEY (hill_id) REFERENCES hills(id)
                    FOREIGN KEY (walk_id) REFERENCES walks(id)
                )
                """
            )
            conn.commit()

    @staticmethod
    def get_hill_id_by_url(url: str) -> int | None:
        """Retrieve hill ID from the database using the hill URL."""
        url = WalkhighlandsData._sanitize_url(url)
        logger.debug(f"Fetching hill ID for URL: {url}")
        db_api = DatabaseAPI()
        with db_api.db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id FROM hills WHERE url = ?
                """,
                (url,),
            )
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                logger.warning(f"Hill with URL {url} not found in the database.")
                return None

    @staticmethod
    def fetch_all_hill_urls() -> list[str]:
        """Fetch all hill URLs from the database."""
        db_api = DatabaseAPI()
        with db_api.db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT url FROM hills
                """
            )
            results = cursor.fetchall()
            return [row[0] for row in results]

    @staticmethod
    def _sanitize_url(url: str) -> str:
        """
        Sanitize the URL to ensure it's well-formed.
        Some contain '%20' at the end
        some incorrectly formed urls https://www.walkhighlands.co.ukhttp://www.walkhighlands.co.uk/munros/am-basteir
        """
        # check for '%20' at the end
        if url.endswith("%20"):
            url = url[:-3]
        # check for duplicated domain
        # only handle until the second occurance of https:// or http://
        if url.count("https://") > 1:
            parts = url.split("https://")
            url = "https://" + parts[-1]
        elif url.count("http://") > 1:
            parts = url.split("http://")
            url = "http://" + parts[-1]

        # if contains both http:// and https://, keep the last one
        if "https://" in url and "http://" in url:
            https_index = url.rfind("https://")
            http_index = url.rfind("http://")
            if https_index > http_index:
                url = url[https_index:]
            else:
                url = url[http_index:]
        url = url.replace("http://", "https://")
        return url

    @staticmethod
    def reset_database(tables: list[str] | None = None) -> None:
        """Reset the database."""
        db_api = DatabaseAPI()
        with db_api.db_connection() as conn:
            cursor = conn.cursor()
            if not tables or "walk_hill_decomposition" in tables:
                logger.info("Dropping and recreating walk_hill_decomposition table.")
                cursor.execute("DROP TABLE IF EXISTS walk_hill_decomposition")
                WalkhighlandsData.create_walk_hill_decomp_table()
            if not tables or "walks" in tables:
                logger.info("Dropping and recreating walks table.")
                cursor.execute("DROP TABLE IF EXISTS walks")
                WalkhighlandsData.create_walk_data_table()
            if not tables or "hills" in tables:
                logger.info("Dropping and recreating hills table.")
                cursor.execute("DROP TABLE IF EXISTS hills")
                WalkhighlandsData.create_hill_data_table()
            conn.commit()
