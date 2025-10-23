from src.users.service import UsersService
from src.users.dtos import LatLon
from unittest.mock import patch
from src.maps.dtos import MapsResponseDTO


def test_check_location_valid():
    valid_location = LatLon(lat=55.9533, lon=-3.1883)  # Edinburgh

    result = UsersService.check_location(valid_location)

    assert result is True


def test_check_location_invalid_latitude_high():
    invalid_location = LatLon(lat=91.0, lon=-3.1883)

    result = UsersService.check_location(invalid_location)

    assert result is False


def test_check_location_invalid_latitude_low():
    invalid_location = LatLon(lat=-91.0, lon=-3.1883)

    result = UsersService.check_location(invalid_location)

    assert result is False


def test_check_location_invalid_longitude_high():
    invalid_location = LatLon(lat=55.9533, lon=181.0)

    result = UsersService.check_location(invalid_location)

    assert result is False


def test_check_location_invalid_longitude_low():
    invalid_location = LatLon(lat=55.9533, lon=-181.0)

    result = UsersService.check_location(invalid_location)

    assert result is False


@patch("src.users.service.UserData")
def test_save_walk_directions_for_user(mock_user_data):
    user_id = 1
    walk_id = 1
    map_response = MapsResponseDTO(
        origin="origin",
        destination="destination",
        distance_meters=1000,
        duration_seconds=3600,
    )

    UsersService.save_walk_directions_for_user(user_id, walk_id, map_response)

    mock_user_data.save_walk_directions.assert_called_once_with(
        user_id, walk_id, map_response
    )
