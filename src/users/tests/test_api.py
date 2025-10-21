import pytest
from unittest.mock import patch
from src.users.api import UsersAPI
from src.users.dtos import LatLon


@patch("src.users.api.UserData")
def test_initialize_users(mock_user_data):
    UsersAPI.initialize_users()

    mock_user_data.create_user_table.assert_called_once()


@patch("src.users.api.UsersService")
@patch("src.users.api.UserData")
@patch("src.users.api.get_lat_lon_from_postcode")
def test_add_user_success(
    mock_get_lat_lon_from_postcode, mock_user_data, mock_users_service
):
    name = "test_user"
    postcode = "EH1 1AA"
    mock_latlon = LatLon(lat=55.9533, lon=-3.1883)
    mock_get_lat_lon_from_postcode.return_value = mock_latlon
    mock_users_service.check_location.return_value = True

    UsersAPI.add_user(name, postcode)

    mock_get_lat_lon_from_postcode.assert_called_once_with(postcode)
    mock_users_service.check_location.assert_called_once_with(mock_latlon)
    mock_user_data.save_user_data.assert_called_once_with(name, mock_latlon)


@patch("src.users.api.UsersService")
@patch("src.users.api.UserData")
@patch("src.users.api.get_lat_lon_from_postcode")
def test_add_user_get_lat_lon_failure(
    mock_get_lat_lon_from_postcode, mock_user_data, mock_users_service
):
    name = "test_user"
    postcode = "INVALID"
    mock_get_lat_lon_from_postcode.side_effect = ValueError("Could not find location")

    UsersAPI.add_user(name, postcode)

    mock_get_lat_lon_from_postcode.assert_called_once_with(postcode)
    mock_users_service.check_location.assert_not_called()
    mock_user_data.save_user_data.assert_not_called()


@patch("src.users.api.UsersService")
@patch("src.users.api.UserData")
@patch("src.users.api.get_lat_lon_from_postcode")
def test_add_user_check_location_failure(
    mock_get_lat_lon_from_postcode, mock_user_data, mock_users_service
):
    name = "test_user"
    postcode = "EH1 1AA"
    mock_latlon = LatLon(lat=55.9533, lon=-3.1883)
    mock_get_lat_lon_from_postcode.return_value = mock_latlon
    mock_users_service.check_location.return_value = False

    UsersAPI.add_user(name, postcode)

    mock_get_lat_lon_from_postcode.assert_called_once_with(postcode)
    mock_users_service.check_location.assert_called_once_with(mock_latlon)
    mock_user_data.save_user_data.assert_not_called()


@patch("src.users.api.UserData")
def test_get_user_location_success(mock_user_data):
    name = "test_user"
    mock_latlon = LatLon(lat=55.9533, lon=-3.1883)
    mock_user_data.fetch_user_location.return_value = mock_latlon

    result = UsersAPI.get_user_location(name)

    assert result == mock_latlon
    mock_user_data.fetch_user_location.assert_called_once_with(name)


@patch("src.users.api.UserData")
def test_get_user_location_not_found(mock_user_data):
    name = "non_existent_user"
    mock_user_data.fetch_user_location.return_value = None

    with pytest.raises(ValueError, match="User not found"):
        UsersAPI.get_user_location(name)
    mock_user_data.fetch_user_location.assert_called_once_with(name)
