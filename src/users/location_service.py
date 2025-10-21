from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from src.users.dtos import LatLon


def get_lat_lon_from_postcode(postcode: str) -> LatLon:
    """
    Given a postcode, return the latitude and longitude using geopy's Nominatim geocoder.
    """
    geolocator = Nominatim(user_agent="location_service")
    search_query = postcode.strip()
    try:
        location = geolocator.geocode(search_query)
        if location and location.latitude and location.longitude:
            return LatLon(lat=location.latitude, lon=location.longitude)
        else:
            raise ValueError(f"Could not find location for postcode: {postcode}")
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        raise ConnectionError(f"Geocoding service error: {e}")
