import pytest
from unittest.mock import patch, MagicMock
from src.users.location_service import get_lat_lon_from_postcode
from src.users.dtos import LatLon
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


@patch('src.users.location_service.Nominatim')
def test_get_lat_lon_from_postcode_success(mock_nominatim):
    mock_geolocator = MagicMock()
    mock_nominatim.return_value = mock_geolocator
    mock_location = MagicMock()
    mock_location.latitude = 55.9533
    mock_location.longitude = -3.1883
    mock_geolocator.geocode.return_value = mock_location

    postcode = "EH1 1AA"
    expected_latlon = LatLon(lat=55.9533, lon=-3.1883)

    result = get_lat_lon_from_postcode(postcode)

    assert result == expected_latlon
    mock_geolocator.geocode.assert_called_once_with(postcode.strip())


@patch('src.users.location_service.Nominatim')
def test_get_lat_lon_from_postcode_not_found(mock_nominatim):
    mock_geolocator = MagicMock()
    mock_nominatim.return_value = mock_geolocator
    mock_geolocator.geocode.return_value = None

    postcode = "INVALIDPOSTCODE"

    with pytest.raises(ValueError, match=f"Could not find location for postcode: {postcode}"):
        get_lat_lon_from_postcode(postcode)
    mock_geolocator.geocode.assert_called_once_with(postcode.strip())


@patch('src.users.location_service.Nominatim')
def test_get_lat_lon_from_postcode_service_error(mock_nominatim):
    mock_geolocator = MagicMock()
    mock_nominatim.return_value = mock_geolocator
    mock_geolocator.geocode.side_effect = GeocoderServiceError("Service unavailable")

    postcode = "EH1 1AA"

    with pytest.raises(ConnectionError, match="Geocoding service error: Service unavailable"):
        get_lat_lon_from_postcode(postcode)
    mock_geolocator.geocode.assert_called_once_with(postcode.strip())


@patch('src.users.location_service.Nominatim')
def test_get_lat_lon_from_postcode_timeout_error(mock_nominatim):
    mock_geolocator = MagicMock()
    mock_nominatim.return_value = mock_geolocator
    mock_geolocator.geocode.side_effect = GeocoderTimedOut("Timed out")

    postcode = "EH1 1AA"

    with pytest.raises(ConnectionError, match="Geocoding service error: Timed out"):
        get_lat_lon_from_postcode(postcode)
    mock_geolocator.geocode.assert_called_once_with(postcode.strip())