import pytest
from src.users.service import UsersService
from src.users.dtos import LatLon


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