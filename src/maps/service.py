import logging
import os

import googlemaps

from src.maps.dtos import MapsResponseDTO

logger = logging.getLogger(__name__)


class MapsService:
    def __init__(self, api_key: str | None = None) -> None:
        """
        Initializes the MapsService.
        :param api_key: Google Maps API key. If not provided, it will be read from the MAPS_API_KEY environment variable.
        """
        if api_key is None:
            api_key = os.getenv("MAPS_API_KEY")
        if not api_key:
            logger.error(
                "Maps API key not found in environment variables or provided directly."
            )
            raise ValueError("Maps API key is required.")
        self.client: googlemaps.Client = googlemaps.Client(key=api_key)

    def get_directions(
        self, origin: str, destination: str, mode: str = "driving"
    ) -> MapsResponseDTO | None:
        """
        Requests directions from Google Maps API and returns a MapsResponseDTO.
        :param origin: Starting location as a string. This can be an address, place name, lat/lon, etc.
        :param destination: Ending location as a string.
        :param mode: Mode of transportation (default is 'driving').
        :return: MapsResponseDTO with distance and duration, or None if an error occurs.
        """
        try:
            directions_result = self.client.directions(  # type: ignore
                origin=origin, destination=destination, mode=mode
            )
            if not directions_result:
                logger.error(
                    "No directions found between %s and %s", origin, destination
                )
                return None
        except googlemaps.exceptions.ApiError:
            logger.exception("Google Maps API error occurred.")
            return None

        distance = int(directions_result[0]["legs"][0]["distance"]["value"])
        duration = int(directions_result[0]["legs"][0]["duration"]["value"])

        return MapsResponseDTO(
            distance_meters=distance,
            duration_seconds=duration,
            origin=origin,
            destination=destination,
        )
