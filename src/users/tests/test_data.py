import pytest
from unittest.mock import patch, MagicMock
import sqlite3
from src.users.data import UserData
from src.users.dtos import LatLon


@pytest.fixture
def mock_db_api():
    with patch("src.users.data.DatabaseAPI") as MockDatabaseAPI:
        mock_instance = MockDatabaseAPI.return_value

        # Create a single in-memory SQLite connection for the entire test
        shared_conn = sqlite3.connect(":memory:")

        # Mock the db_connection method to return a context manager
        # that always yields the shared_conn
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = shared_conn
        mock_context_manager.__exit__.return_value = None
        mock_instance.db_connection.return_value = mock_context_manager

        yield mock_instance

        # Close the shared connection after the test
        shared_conn.close()


def test_create_user_table(mock_db_api):
    UserData.create_user_table()

    conn = mock_db_api.db_connection.return_value.__enter__.return_value
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print(f"Columns: {columns}")  # Debug print
    column_names = [col[1] for col in columns]
    assert "id" in column_names
    assert "name" in column_names
    assert "location" in column_names
    assert "created_at" in column_names


def test_save_and_fetch_user_data(mock_db_api):
    UserData.create_user_table()
    name = "test_user"
    location = LatLon(lat=56.0, lon=-4.0)

    UserData.save_user_data(name, location)
    _, fetched_location = UserData.fetch_user_location(name)

    assert fetched_location == location


def test_fetch_user_location_not_found(mock_db_api):
    UserData.create_user_table()
    name = "non_existent_user"

    fetched_location = UserData.fetch_user_location(name)

    assert fetched_location is None

    location = LatLon(lat=56.123, lon=-4.456)
    expected_string = "56.123,-4.456"

    result = UserData._get_lat_lon_string(location)

    assert result == expected_string


def test_parse_lat_lon_string():
    location_string = "56.123,-4.456"
    expected_location = LatLon(lat=56.123, lon=-4.456)

    result = UserData._parse_lat_lon_string(location_string)

    assert result == expected_location


def test_save_walk_directions(mock_db_api):
    UserData.create_user_table()
    UserData.create_user_walk_directions_table()

    user_id = 1
    walk_id = 1
    map_response = MagicMock()
    map_response.distance_meters = 1000
    map_response.duration_seconds = 3600

    UserData.save_walk_directions(user_id, walk_id, map_response)

    conn = mock_db_api.db_connection.return_value.__enter__.return_value
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, walk_id, distance, duration FROM user_walk_directions WHERE user_id = ? AND walk_id = ?",
        (user_id, walk_id),
    )
    result = cursor.fetchone()

    assert result is not None
    assert result[0] == user_id
    assert result[1] == walk_id
    assert result[2] == map_response.distance_meters
    assert result[3] == map_response.duration_seconds


def test_save_walk_directions_duplicate(mock_db_api):
    UserData.create_user_table()
    UserData.create_user_walk_directions_table()

    user_id = 1
    walk_id = 1
    map_response = MagicMock()
    map_response.distance_meters = 1000
    map_response.duration_seconds = 3600

    # First save should be successful
    UserData.save_walk_directions(user_id, walk_id, map_response)

    # Second save should trigger the integrity error and log a warning
    with patch("src.users.data.logger.warning") as mock_warning:
        UserData.save_walk_directions(user_id, walk_id, map_response)
        mock_warning.assert_called_once_with(
            "Directions for this user and walk already exist.",
            extra={"user_id": user_id, "walk_id": walk_id},
        )
