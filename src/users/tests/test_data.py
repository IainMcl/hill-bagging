import pytest
from unittest.mock import patch, MagicMock
import sqlite3
from src.users.data import UserData
from src.users.dtos import (
    LatLon,
)


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


def test_get_user_walks_travel_info(mock_db_api):
    conn = mock_db_api.db_connection.return_value.__enter__.return_value
    cursor = conn.cursor()

    # Create tables
    UserData.create_user_table()
    UserData.create_user_walk_directions_table()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS walks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, url TEXT, grade INTEGER,
            bog_factor INTEGER, user_rating REAL, distance REAL, time REAL,
            ascent INTEGER, start_grid_ref TEXT, start_location TEXT
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS hills (
            id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, name TEXT,
            region TEXT, altitude INTEGER
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS walk_hill_decomposition (
            id INTEGER PRIMARY KEY AUTOINCREMENT, hill_id INTEGER, walk_id INTEGER
        )
    """
    )

    # Insert test data
    cursor.execute(
        "INSERT INTO users (id, name, location) VALUES (1, 'test_user', '56.0,-4.0')"
    )
    cursor.execute(
        "INSERT INTO walks (id, title, url, grade, bog_factor, user_rating, distance, time, ascent, start_grid_ref, start_location) VALUES (1, 'Test Walk 1', 'http://walk1.com', 1, 1, 1, 1.5, 1.25, 100, 'NN123456', 'http://start.com/1')"
    )
    cursor.execute(
        "INSERT INTO walks (id, title, url, grade, bog_factor, user_rating, distance, time, ascent, start_grid_ref, start_location) VALUES (2, 'Test Walk 2', 'http://walk2.com', 1, 1, 1, 2.0, 2.5, 200, 'NN654321', 'http://start.com/2')"
    )
    cursor.execute(
        "INSERT INTO hills (id, name, url, region, altitude) VALUES (101, 'Test Hill 1', 'http://hill1.com', 'Region 1', 1000)"
    )
    cursor.execute(
        "INSERT INTO hills (id, name, url, region, altitude) VALUES (102, 'Test Hill 2', 'http://hill2.com', 'Region 1', 1100)"
    )
    cursor.execute(
        "INSERT INTO walk_hill_decomposition (walk_id, hill_id) VALUES (1, 101)"
    )
    cursor.execute(
        "INSERT INTO walk_hill_decomposition (walk_id, hill_id) VALUES (1, 102)"
    )
    cursor.execute(
        "INSERT INTO user_walk_directions (user_id, walk_id, distance, duration) VALUES (1, 1, 100, 1000)"
    )
    cursor.execute(
        "INSERT INTO user_walk_directions (user_id, walk_id, distance, duration) VALUES (1, 2, 200, 2000)"
    )
    conn.commit()

    result = UserData.get_user_walks_travel_info(user_id=1)

    assert len(result) == 2

    walk_1_info = next((item for item in result if item.walk_info.walk_id == 1), None)
    assert walk_1_info is not None
    assert walk_1_info.user_id == 1
    assert walk_1_info.walk_info.walk_name == "Test Walk 1"
    assert walk_1_info.walk_info.number_of_hills == 2
    assert set(walk_1_info.walk_info.hills) == {"Test Hill 1", "Test Hill 2"}
    assert walk_1_info.walk_info.walk_distance_meters == 1500
    assert walk_1_info.walk_info.walk_ascent_meters == 100
    assert walk_1_info.walk_info.walk_duration_seconds == 4500
    assert walk_1_info.walk_info.walk_url == "http://walk1.com"
    assert walk_1_info.walk_info.walk_start_location == "http://start.com/1"
    assert walk_1_info.travel_info.distance_meters == 100
    assert walk_1_info.travel_info.duration_seconds == 1000

    walk_2_info = next((item for item in result if item.walk_info.walk_id == 2), None)
    assert walk_2_info is not None
    assert walk_2_info.user_id == 1
    assert walk_2_info.walk_info.walk_name == "Test Walk 2"
    assert walk_2_info.walk_info.number_of_hills == 0
    assert walk_2_info.walk_info.hills == []
    assert walk_2_info.walk_info.walk_distance_meters == 2000
    assert walk_2_info.walk_info.walk_ascent_meters == 200
    assert walk_2_info.walk_info.walk_duration_seconds == 9000
    assert walk_2_info.walk_info.walk_url == "http://walk2.com"
    assert walk_2_info.walk_info.walk_start_location == "http://start.com/2"
    assert walk_2_info.travel_info.distance_meters == 200
    assert walk_2_info.travel_info.duration_seconds == 2000
