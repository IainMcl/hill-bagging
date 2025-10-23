import pytest
from unittest.mock import patch
from src.maps.service import MapsService
from src.maps.dtos import MapsResponseDTO
import googlemaps


@patch("os.getenv")
def test_init_no_api_key(mock_getenv):
    mock_getenv.return_value = None
    with pytest.raises(ValueError, match="Maps API key is required."):
        MapsService()


@patch("googlemaps.Client")
def test_get_directions_success(mock_client):
    mock_directions_result = [
        {
            "legs": [
                {
                    "distance": {"value": 1000},
                    "duration": {"value": 3600},
                }
            ]
        }
    ]
    mock_client.return_value.directions.return_value = mock_directions_result

    service = MapsService(api_key="test_key")
    result = service.get_directions(origin="origin", destination="destination")

    assert isinstance(result, MapsResponseDTO)
    assert result.distance_meters == 1000
    assert result.duration_seconds == 3600
    assert result.origin == "origin"
    assert result.destination == "destination"


@patch("googlemaps.Client")
def test_get_directions_no_results(mock_client):
    mock_client.return_value.directions.return_value = []

    service = MapsService(api_key="test_key")
    result = service.get_directions(origin="origin", destination="destination")

    assert result is None


@patch("googlemaps.Client")
def test_get_directions_api_error(mock_client):
    mock_client.return_value.directions.side_effect = googlemaps.exceptions.ApiError(
        "error"
    )

    service = MapsService(api_key="test_key")
    result = service.get_directions(origin="origin", destination="destination")

    assert result is None
