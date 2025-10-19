import logging
import os

from src.database.services.database_service_interface import DatabaseServiceInterface
from src.database.services.sqliteservice import SQLiteService
from src.database.services.postgressqlservice import PostgreSQLService


logger = logging.getLogger(__name__)


class DatabaseAPI:
    def __init__(self):
        self.interface: DatabaseServiceInterface = self._get_service()

    def _get_service(self) -> DatabaseServiceInterface:
        db_type = os.getenv("DB_TYPE", "sqlite").lower()
        match db_type:
            case "sqlite":
                db_path = os.getenv("SQLITE_DB_PATH", "database.sqlite")
                return SQLiteService(db_path)
            case "postgresql":
                host = os.getenv("DB_HOST")
                port = os.getenv("DB_PORT")
                user = os.getenv("DB_USER")
                password = os.getenv("DB_PASSWORD")
                database = os.getenv("DB_NAME")
                return PostgreSQLService(host, port, user, password, database)
            case _:
                raise ValueError(f"Unsupported DB_TYPE: {db_type}")

    def db_connection(self):
        """
        Context manager for database connection.
        """
        return self.interface.db_connection()
