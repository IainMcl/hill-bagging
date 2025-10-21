import pytest
from unittest.mock import patch, MagicMock
from database.api import DatabaseAPI


@patch("database.api.PostgreSQLService")
@patch("database.api.SQLiteService")
@patch("os.getenv")
class TestDatabaseAPI:
    def test_get_service_sqlite_default(
        self, mock_getenv, mock_sqlite_service, mock_postgresql_service
    ):
        mock_getenv.side_effect = lambda key, default=None: {"DB_TYPE": "sqlite"}.get(
            key, default
        )

        api = DatabaseAPI()
        service = api.interface

        mock_getenv.assert_any_call("DB_TYPE", "sqlite")
        mock_getenv.assert_any_call("SQLITE_DB_PATH", "database.sqlite")
        mock_sqlite_service.assert_called_once_with("database.sqlite")
        assert service is mock_sqlite_service.return_value
        mock_postgresql_service.assert_not_called()

    def test_get_service_sqlite_custom_path(
        self, mock_getenv, mock_sqlite_service, mock_postgresql_service
    ):
        mock_getenv.side_effect = lambda key, default=None: {
            "DB_TYPE": "sqlite",
            "SQLITE_DB_PATH": "custom.db",
        }.get(key, default)

        api = DatabaseAPI()
        service = api.interface

        mock_getenv.assert_any_call("DB_TYPE", "sqlite")
        mock_getenv.assert_any_call("SQLITE_DB_PATH", "database.sqlite")
        mock_sqlite_service.assert_called_once_with("custom.db")
        assert service is mock_sqlite_service.return_value
        mock_postgresql_service.assert_not_called()

    def test_get_service_postgresql_success(
        self, mock_getenv, mock_sqlite_service, mock_postgresql_service
    ):
        mock_getenv.side_effect = lambda key, default=None: {
            "DB_TYPE": "postgresql",
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_USER": "user",
            "DB_PASSWORD": "password",
            "DB_NAME": "database",
        }.get(key, default)

        api = DatabaseAPI()
        service = api.interface

        mock_getenv.assert_any_call("DB_TYPE", "sqlite")  # Called with default first
        mock_getenv.assert_any_call("DB_HOST")
        mock_getenv.assert_any_call("DB_PORT")
        mock_getenv.assert_any_call("DB_USER")
        mock_getenv.assert_any_call("DB_PASSWORD")
        mock_getenv.assert_any_call("DB_NAME")
        mock_postgresql_service.assert_called_once_with(
            "localhost", "5432", "user", "password", "database"
        )
        assert service is mock_postgresql_service.return_value
        mock_sqlite_service.assert_not_called()

    def test_get_service_unsupported_type(
        self, mock_getenv, mock_sqlite_service, mock_postgresql_service
    ):
        mock_getenv.side_effect = lambda key, default=None: {
            "DB_TYPE": "unsupported"
        }.get(key, default)

        with pytest.raises(ValueError, match="Unsupported DB_TYPE: unsupported"):
            DatabaseAPI()
        mock_sqlite_service.assert_not_called()
        mock_postgresql_service.assert_not_called()

    def test_db_connection(
        self, mock_getenv, mock_sqlite_service, mock_postgresql_service
    ):
        mock_getenv.side_effect = lambda key, default=None: {"DB_TYPE": "sqlite"}.get(
            key, default
        )
        mock_sqlite_service.return_value.db_connection.return_value = MagicMock()

        api = DatabaseAPI()
        with api.db_connection() as conn:
            conn.some_method()

        mock_sqlite_service.return_value.db_connection.assert_called_once()
        conn.some_method.assert_called_once()
