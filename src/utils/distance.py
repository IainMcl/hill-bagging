def kilometers_to_meters(kilometers: float) -> int:
    """Convert kilometers to meters."""
    return int(kilometers * 1000)


def meters_to_kilometers(meters: int) -> float:
    """Convert meters to kilometers."""
    return meters / 1000.0


def user_display_distance(
    *, distance_km: float | None = None, distance_m: int | None = None
) -> str:
    """Convert distance in kilometers or meters to a user-friendly string in kilometers and meters."""
    if distance_km is None and distance_m is None:
        raise ValueError("Either distance_km or distance_m must be provided.")
    if distance_km is not None:
        total_meters = int(distance_km * 1000)
    elif distance_m is not None:
        total_meters = distance_m
    else:
        raise ValueError("Either distance_km or distance_m must be provided.")
    kilometers = total_meters // 1000
    meters = total_meters % 1000
    if kilometers > 0:
        return f"{kilometers} km {meters} m"
    else:
        return f"{meters} m"
