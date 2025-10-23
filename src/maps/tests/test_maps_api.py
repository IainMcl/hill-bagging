from unittest.mock import patch, MagicMock
from src.maps.api import MapsApi
from src.maps.dtos import MapsResponseDTO


@patch("src.maps.api.MapsService")
def test_get_driving_distance_and_time(mock_maps_service):
    mock_service_instance = MagicMock()
    mock_maps_service.return_value = mock_service_instance

    expected_response = MapsResponseDTO(
        origin="origin",
        destination="destination",
        distance_meters=1000,
        duration_seconds=3600,
    )
    mock_service_instance.get_directions.return_value = expected_response

    result = MapsApi.get_driving_distance_and_time(
        origin="origin", destination="destination"
    )

    assert result == expected_response
    mock_service_instance.get_directions.assert_called_once_with(
        origin="origin", destination="destination", mode="driving"
    )
