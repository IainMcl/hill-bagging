import logging
import sqlite3
import os
from src.database.services.database_service_interface import DatabaseServiceInterface

logger = logging.getLogger(__name__)


class SQLiteService(DatabaseServiceInterface):
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
        if not os.path.exists(db_path):
            logger.warning(
                "Database file does not exist. It will be created upon connection.",
                extra={"db_path": db_path},
            )
            self._create_database()

    def _create_database(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            logger.debug(
                "Created new SQLite database.", extra={"db_path": self.db_path}
            )
            self.connection.close()
            self.connection = None
        except sqlite3.Error as e:
            logger.error("Failed to create database", extra={"error": e})
            raise

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            logger.debug(
                "Connected to SQLite database.", extra={"db_path": self.db_path}
            )
        except sqlite3.Error as e:
            logger.error("Failed to connect to database", extra={"error": e})
            raise

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.debug("Disconnected from SQLite database")

    def execute_query(self, query):
        if not self.connection:
            raise Exception("Database not connected")
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
            results = cursor.fetchall()
            logger.info("Executed query", extra={"query": query})
            return results
        except sqlite3.Error as e:
            logger.error("Failed to execute query", extra={"error": e})
            raise

    def db_connection(self):
        """
        Context manager for database connection.
        """

        class DBConnectionContextManager:
            def __init__(self, service):
                self.service = service

            def __enter__(self):
                self.service.connect()
                return self.service.connection

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.service.disconnect()

        return DBConnectionContextManager(self)
