from src.users.dtos import UserWalkTravelInfo, WalkInfo, TravelInfo


def create_user_walk_travel_info(
    user_id: int = 1,
    walk_id: int = 1,
    walk_name: str = "Test Walk",
    walk_start_location: str = "55.9533,-3.1883",
    walk_ascent_meters: int = 500,
    walk_distance_meters: int = 10000,
    walk_duration_seconds: int = 18000,
    walk_url: str = "http://test.com",
    number_of_hills: int = 1,
    hills: list[str] | None = None,
    distance_meters: int = 20000,
    duration_seconds: int = 3600,
    total_time_seconds: int = 21600,
) -> UserWalkTravelInfo:
    if hills is None:
        hills = ["Test Hill"]
    return UserWalkTravelInfo(
        user_id=user_id,
        walk_info=WalkInfo(
            walk_id=walk_id,
            walk_name=walk_name,
            walk_start_location=walk_start_location,
            walk_ascent_meters=walk_ascent_meters,
            walk_distance_meters=walk_distance_meters,
            walk_duration_seconds=walk_duration_seconds,
            walk_url=walk_url,
            number_of_hills=number_of_hills,
            hills=hills,
        ),
        travel_info=TravelInfo(
            distance_meters=distance_meters,
            duration_seconds=duration_seconds,
        ),
        total_time_seconds=total_time_seconds,
    )
