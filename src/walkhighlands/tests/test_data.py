import pytest
from unittest.mock import patch, MagicMock
import sqlite3
from src.walkhighlands.data.hill_data import WalkhighlandsData
from src.walkhighlands.dtos import WalkData


@pytest.fixture
def mock_db_api():
    with patch("src.walkhighlands.data.hill_data.DatabaseAPI") as MockDatabaseAPI:
        mock_instance = MockDatabaseAPI.return_value
        shared_conn = sqlite3.connect(":memory:")
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = shared_conn
        mock_context_manager.__exit__.return_value = None
        mock_instance.db_connection.return_value = mock_context_manager
        yield mock_instance
        shared_conn.close()


def test_insert_walk_duplicate_hill_decomposition(mock_db_api):
    WalkhighlandsData.create_walk_data_table()
    WalkhighlandsData.create_hill_data_table()
    WalkhighlandsData.create_walk_hill_decomp_table()

    walk_data = WalkData(
        title="Test Walk",
        url="http://test.com",
        grade=1,
        bog_factor=1,
        user_rating=1,
        distance_km=1,
        duration_hr=1,
        ascent_m=1,
        start_grid_ref="NN123456",
        start_location="somewhere",
        hill_ids=[1, 1],  # Duplicate hill_id
    )

    with patch("src.walkhighlands.data.hill_data.logger.warning") as mock_warning:
        WalkhighlandsData.insert_walk(walk_data)
        mock_warning.assert_called_once_with(
            "Duplicate entry for walk_hill_decomposition.",
            extra={"hill_id": 1, "walk_id": 1},
        )
