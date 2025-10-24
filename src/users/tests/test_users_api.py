import pytest
from src.users.tests.factories import create_user_walk_travel_info
from unittest.mock import patch
from src.users.api import UsersAPI
from src.users.dtos import LatLon
from src.walkhighlands.dtos import WalkStartLocationDTO
from src.maps.dtos import MapsResponseDTO


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
    mock_user_data.fetch_user_location.return_value = (1, mock_latlon)

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


@patch("src.users.api.UsersAPI._directions_already_saved", return_value=False)
@patch("src.users.api.UsersService")
@patch("src.users.api.MapsApi")
@patch("src.users.api.WalkhighlandsAPI")
@patch("src.users.api.UserData")
def test_get_walk_directions_for_user(
    mock_user_data,
    mock_walkhighlands_api,
    mock_maps_api,
    mock_users_service,
    mock_directions_already_saved,
):
    user = "test_user"
    user_id = 1
    user_location = LatLon(lat=55.84901, lon=-3.14373)
    mock_user_data.fetch_user_location.return_value = (user_id, user_location)

    walk_location = WalkStartLocationDTO(
        walk_id=1, walk_start_location="56.90890,-4.23660"
    )
    mock_walkhighlands_api.get_walk_start_locations.return_value = [walk_location]

    map_response = MapsResponseDTO(
        origin="55.84901,-3.14373",
        destination="56.90890,-4.23660",
        distance_meters=179939,
        duration_seconds=7461,
    )
    mock_maps_api.get_driving_distance_and_time.return_value = map_response

    UsersAPI.get_walk_directions_for_user(user)

    mock_user_data.fetch_user_location.assert_called_once_with(user)
    mock_walkhighlands_api.get_walk_start_locations.assert_called_once()
    mock_maps_api.get_driving_distance_and_time.assert_called_once_with(
        origin="55.84901,-3.14373", destination="56.90890,-4.23660"
    )
    mock_users_service.save_walk_directions_for_user.assert_called_once_with(
        user_id, walk_location.walk_id, map_response
    )


@patch("src.users.api.UsersAPI._directions_already_saved", return_value=True)
@patch("src.users.api.UsersService")
@patch("src.users.api.MapsApi")
@patch("src.users.api.WalkhighlandsAPI")
@patch("src.users.api.UserData")
def test_get_walk_directions_for_user_skips_existing(
    mock_user_data,
    mock_walkhighlands_api,
    mock_maps_api,
    mock_users_service,
    mock_directions_already_saved,
):
    user = "test_user"
    user_id = 1
    user_location = LatLon(lat=55.84901, lon=-3.14373)
    mock_user_data.fetch_user_location.return_value = (user_id, user_location)

    walk_location = WalkStartLocationDTO(
        walk_id=1, walk_start_location="56.90890,-4.23660"
    )
    mock_walkhighlands_api.get_walk_start_locations.return_value = [walk_location]

    UsersAPI.get_walk_directions_for_user(user)

    mock_user_data.fetch_user_location.assert_called_once_with(user)
    mock_walkhighlands_api.get_walk_start_locations.assert_called_once()
    mock_maps_api.get_driving_distance_and_time.assert_not_called()
    mock_users_service.save_walk_directions_for_user.assert_not_called()


@patch("src.users.api.UserData")
def test_directions_already_saved_true(mock_user_data):
    mock_user_data.check_walk_directions_exist.return_value = True
    result = UsersAPI._directions_already_saved(1, 1)
    assert result is True
    mock_user_data.check_walk_directions_exist.assert_called_once_with(1, 1)


@patch("src.users.api.UsersService")
@patch("src.users.api.UserData")
def test_get_optimal_user_routes(mock_user_data, mock_users_service):
    user = "test_user"
    user_id = 1
    mock_user_data.get_user_id_for_name.return_value = user_id

    walk_infos = [
        create_user_walk_travel_info(
            walk_id=1, number_of_hills=1, total_time_seconds=1000
        ),
        create_user_walk_travel_info(
            walk_id=2, number_of_hills=0, total_time_seconds=500
        ),
        create_user_walk_travel_info(
            walk_id=3, number_of_hills=2, total_time_seconds=2000
        ),
    ]
    mock_users_service.calculate_user_total_times.return_value = walk_infos

    UsersAPI.get_optimal_user_routes(user, 10, ascending=True)

    mock_users_service.display_user_walk_travel_info.assert_called_once()
    args, _ = mock_users_service.display_user_walk_travel_info.call_args
    displayed_walks = args[0]

    assert len(displayed_walks) == 2
    assert displayed_walks[0].walk_info.walk_id == 1
    assert displayed_walks[1].walk_info.walk_id == 3

    UsersAPI.get_optimal_user_routes(user, 10, ascending=False)
    args, _ = mock_users_service.display_user_walk_travel_info.call_args
    displayed_walks = args[0]
    assert displayed_walks[0].walk_info.walk_id == 3
    assert displayed_walks[1].walk_info.walk_id == 1
