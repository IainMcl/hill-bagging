import pytest
from unittest.mock import patch, MagicMock
import sqlite3
from database.services.sqliteservice import SQLiteService


class TestSQLiteService:
    @patch("os.path.exists")
    @patch("sqlite3.connect")
    def test_init_db_does_not_exist(self, mock_sqlite_connect, mock_os_path_exists):
        mock_os_path_exists.return_value = False
        mock_connect_instance = MagicMock()
        mock_sqlite_connect.return_value = mock_connect_instance

        service = SQLiteService("test.db")

        mock_os_path_exists.assert_called_once_with("test.db")
        mock_sqlite_connect.assert_called_once_with("test.db")
        mock_connect_instance.close.assert_called_once()
        assert service.db_path == "test.db"
        assert service.connection is None

    @patch("os.path.exists")
    @patch("sqlite3.connect")
    def test_init_db_exists(self, mock_sqlite_connect, mock_os_path_exists):
        mock_os_path_exists.return_value = True

        service = SQLiteService("test.db")

        mock_os_path_exists.assert_called_once_with("test.db")
        mock_sqlite_connect.assert_not_called()
        assert service.db_path == "test.db"
        assert service.connection is None

    @patch("os.path.exists", return_value=False)
    @patch("sqlite3.connect", side_effect=sqlite3.Error("DB Error"))
    def test_create_database_error(self, mock_sqlite_connect, mock_os_path_exists):
        with pytest.raises(sqlite3.Error, match="DB Error"):
            SQLiteService("test.db")

        mock_os_path_exists.assert_called_once_with("test.db")
        mock_sqlite_connect.assert_called_once_with("test.db")

    @patch("database.services.sqliteservice.SQLiteService._create_database")
    @patch("sqlite3.connect")
    def test_connect_success(self, mock_sqlite_connect, mock_create_database):
        service = SQLiteService("test.db")
        service.connect()

        mock_sqlite_connect.assert_called_once_with("test.db")
        assert service.connection is not None

    @patch("database.services.sqliteservice.SQLiteService._create_database")
    @patch("sqlite3.connect", side_effect=sqlite3.Error("Connection Error"))
    def test_connect_error(self, mock_sqlite_connect, mock_create_database):
        service = SQLiteService("test.db")
        with pytest.raises(sqlite3.Error, match="Connection Error"):
            service.connect()

        mock_sqlite_connect.assert_called_once_with("test.db")
        assert service.connection is None

    @patch("database.services.sqliteservice.SQLiteService._create_database")
    def test_disconnect_success(self, mock_create_database):
        service = SQLiteService("test.db")
        mock_connection = MagicMock()
        service.connection = mock_connection
        service.disconnect()

        mock_connection.close.assert_called_once()
        assert service.connection is None

    @patch("database.services.sqliteservice.SQLiteService._create_database")
    def test_disconnect_not_connected(self, mock_create_database):
        service = SQLiteService("test.db")
        service.disconnect()

        assert service.connection is None

    @patch("database.services.sqliteservice.SQLiteService._create_database")
    def test_execute_query_success_with_results(self, mock_create_database):
        service = SQLiteService("test.db")
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("row1",), ("row2",)]
        service.connection = MagicMock()
        service.connection.cursor.return_value = mock_cursor

        results = service.execute_query("SELECT * FROM test")

        service.connection.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test")
        service.connection.commit.assert_called_once()
        mock_cursor.fetchall.assert_called_once()
        assert results == [("row1",), ("row2",)]

    @patch("database.services.sqliteservice.SQLiteService._create_database")
    def test_execute_query_success_no_results(self, mock_create_database):
        service = SQLiteService("test.db")
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        service.connection = MagicMock()
        service.connection.cursor.return_value = mock_cursor

        results = service.execute_query("SELECT * FROM test")

        service.connection.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test")
        service.connection.commit.assert_called_once()
        mock_cursor.fetchall.assert_called_once()
        assert results == []

    @patch("database.services.sqliteservice.SQLiteService._create_database")
    def test_execute_query_error(self, mock_create_database):
        service = SQLiteService("test.db")
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = sqlite3.Error("Query Error")
        service.connection = MagicMock()
        service.connection.cursor.return_value = mock_cursor

        with pytest.raises(sqlite3.Error, match="Query Error"):
            service.execute_query("SELECT * FROM test")

        service.connection.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test")
        service.connection.commit.assert_not_called()

    @patch("database.services.sqliteservice.SQLiteService._create_database")
    def test_execute_query_not_connected(self, mock_create_database):
        service = SQLiteService("test.db")
        with pytest.raises(Exception, match="Database not connected"):
            service.execute_query("SELECT * FROM test")
