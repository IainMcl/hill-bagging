import logging
import os

from src.database.services.database_service_interface import DatabaseServiceInterface

logger = logging.getLogger(__name__)


class PostgreSQLService(DatabaseServiceInterface):
    def __init__(
        self,
        host: str | None = None,
        port: str | None = None,
        user: str | None = None,
        password: str | None = None,
        database: str | None = None,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        if not all([host, port, user, password, database]):
            logger.info("Loading database configuration from environment variables")

    def _load_config_from_env(self) -> None:
        """
        Load database configuration from environment variables.
        """
        self.host = os.getenv("DB_HOST", self.host)
        self.port = os.getenv("DB_PORT", self.port)
        self.user = os.getenv("DB_USER", self.user)
        self.password = os.getenv("DB_PASSWORD", self.password)
        self.database = os.getenv("DB_NAME", self.database)
        if not all([self.host, self.port, self.user, self.password, self.database]):
            raise ValueError("Database configuration is incomplete.")

    def connect(self):
        return "Connected to the database"

    def disconnect(self):
        return "Disconnected from the database"
