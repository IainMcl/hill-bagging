from src.users.service import UsersService
from src.users.tests.factories import create_user_walk_travel_info
from src.users.dtos import LatLon
from unittest.mock import patch


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


@patch("builtins.print")
def test_display_user_walk_travel_info(mock_print):
    walk_travel_info = create_user_walk_travel_info()

    UsersService.display_user_walk_travel_info([walk_travel_info])

    expected_calls = [
        "==================================================",
        "Walk Name: Test Walk",
        "URL: http://test.com",
        "Start Location: 55.9533,-3.1883",
        "Distance: 10.00 km",
        "Ascent: 500 m",
        "Duration: 5h 0m",
        "Number of Hills: 1",
        "Hills: Test Hill",
        "--------------------------------------------------",
        "Travel Information:",
        "  Travel Time: 1h 0m",
        "  Travel Distance: 20.00 km",
        "--------------------------------------------------",
        "Total Trip Information:",
        "  Total Time: 6h 0m",
        "==================================================",
    ]
    mock_print.assert_any_call(expected_calls[0])
    mock_print.assert_any_call(expected_calls[1])
    mock_print.assert_any_call(expected_calls[2])
    mock_print.assert_any_call(expected_calls[3])
    mock_print.assert_any_call(expected_calls[4])
    mock_print.assert_any_call(expected_calls[5])
    mock_print.assert_any_call(expected_calls[6])
    mock_print.assert_any_call(expected_calls[7])
    mock_print.assert_any_call(expected_calls[8])
    mock_print.assert_any_call(expected_calls[9])
    mock_print.assert_any_call(expected_calls[10])
    mock_print.assert_any_call(expected_calls[11])
    mock_print.assert_any_call(expected_calls[12])
    mock_print.assert_any_call(expected_calls[13])
    mock_print.assert_any_call(expected_calls[14])
    mock_print.assert_any_call(expected_calls[15])
