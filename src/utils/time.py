def seconds_to_hours(seconds: int) -> float:
    """Convert seconds to hours."""
    return seconds / 3600.0


def hours_to_seconds(hours: float) -> int:
    """Convert hours to seconds."""
    return int(hours * 3600)


def user_display_time_hours(
    *, time_hours: float | None = None, time_seconds: int | None = None
) -> str:
    """Convert time in hours or seconds to a user-friendly string in hours and minutes."""
    if time_hours is None and time_seconds is None:
        raise ValueError("Either time_hours or time_seconds must be provided.")
    if time_hours is not None:
        total_minutes = int(time_hours * 60)
    elif time_seconds is not None:
        total_minutes = int(time_seconds / 60)
    else:
        raise ValueError("Either time_hours or time_seconds must be provided.")
    hours = total_minutes // 60
    minutes = total_minutes % 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"
