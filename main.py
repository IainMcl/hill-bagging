from src.walkhighlands.api import WalkhighlandsAPI
from src.users.service import UsersService
from src.exporter.csv_exporter import CsvExporter
from src.users.data import UserData

from src.users.api import UsersAPI
import argparse
import sys
from src.utils.logging_config import init_logging
import logging
from dotenv import load_dotenv

load_dotenv()

init_logging()
logger = logging.getLogger(__name__)


def initialize(args):
    logger.info("Initializing with arguments", extra={"cli_args": vars(args)})
    WalkhighlandsAPI.initialize_app()
    UsersAPI.initialize_users()
    logger.info("Initialization complete.")


def fetch_hills_data(args):
    logger.info("Fetching Munro data with arguments", extra={"cli_args": vars(args)})
    munros = WalkhighlandsAPI.get_munros()
    WalkhighlandsAPI.save_munros(munros)


def fetch_walks(args):
    logger.info("Fetching walks with arguments", extra={"cli_args": vars(args)})
    hill_urls = WalkhighlandsAPI.get_hill_urls()
    for hill_url in hill_urls:
        walks = WalkhighlandsAPI.get_walks_for_hill(hill_url)
        for walk in walks:
            walk_data = WalkhighlandsAPI.get_walk_data(walk.url)
            # save
            if walk_data:
                WalkhighlandsAPI.save_walk(walk_data)
            else:
                logger.error("Failed to fetch walk data", extra={"walk_url": walk.url})
        # time.sleep(1)  # Be polite and avoid overwhelming the server


def reset_database(args):
    logger.info("Resetting database with arguments", extra={"cli_args": vars(args)})
    WalkhighlandsAPI.reset_database(args.tables)
    logger.info("Database reset complete.")


def add_user(args):
    logger.info("Adding user with arguments", extra={"cli_args": vars(args)})
    UsersAPI.add_user(args.name, args.postcode)


def get_walk_directions_for_user(args):
    logger.info("Getting walk directions for user", extra={"cli_args": vars(args)})
    UsersAPI.get_walk_directions_for_user(args.user)


def directions(args):
    from src.maps.api import MapsApi

    dirs = MapsApi.get_driving_distance_and_time(args.start, args.end)
    logger.info("Directions fetched", extra={"directions": dirs.model_dump()})


def get_optimal_user_routes(args):
    logger.info("Getting optimal routes for user", extra={"cli_args": vars(args)})
    UsersAPI.get_optimal_user_routes(args.users, args.number_of_routes, args.ascending)


def export_user_routes_to_csv(args):
    logger.info("Exporting user routes to CSV", extra={"cli_args": vars(args)})
    user_id = UserData.get_user_id_for_name(args.user)
    if not user_id:
        logger.error("User not found", extra={"user": args.user})
        return
    walk_travel_infos = UsersService.calculate_user_total_times(user_id)
    CsvExporter.export_user_walk_travel_info(args.user, walk_travel_infos, args.output)


def main():
    parser = argparse.ArgumentParser(
        description="Walkhighlands CLI Tool",
        usage="""
    main.py <command> [<args>]

    Commands:
        init: Initialize the application.
        fetch-hills: Fetch and store Munro data.
        fetch-walks: Fetch walks for a specific hill.
        reset-db: Reset the database.
        add-user: Add a new user.
        directions: test to get driving directions
        walk-directions: Get walking directions for a user to a walk.
        optimal-routes: Get optimal routes for user walk.
        export-csv: Export user walk data to a CSV file.
    """,
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True
    subparsers.add_parser("init", help="Initialize the application")
    subparsers.add_parser("fetch-hills", help="Fetch and store Munro data")
    subparsers.add_parser("fetch-walks", help="Fetch walks for a specific hill")
    reset_db_parser = subparsers.add_parser("reset-db", help="Reset the database")
    reset_db_parser.add_argument(
        "--tables",
        nargs="+",
        choices=["hills", "walks", "walk_hill_decomposition"],
        help="Specify which tables to reset.",
    )
    user_parser = subparsers.add_parser("add-user", help="Add a new user")
    user_parser.add_argument("--name", type=str, required=True, help="Name of the user")
    user_parser.add_argument(
        "--postcode", type=str, required=True, help="Postcode of the user"
    )
    directions_parser = subparsers.add_parser(
        "directions", help="Get driving directions"
    )
    directions_parser.add_argument(
        "--start",
        type=str,
        required=True,
        help="Starting location in 'lat,lon' format",
    )
    directions_parser.add_argument(
        "--end",
        type=str,
        required=True,
        help="Ending location in 'lat,lon' format",
    )
    walk_directions_for_user_parser = subparsers.add_parser(
        "walk-directions", help="Get walking directions for a user to a walk"
    )
    walk_directions_for_user_parser.add_argument(
        "--user", type=str, required=True, help="User's name"
    )
    optimal_routes_parser = subparsers.add_parser(
        "optimal-routes", help="Get optimal routes for user walks"
    )
    optimal_routes_parser.add_argument(
        "--users", type=str, required=True, help="User's name"
    )
    optimal_routes_parser.add_argument(
        "--number_of_routes",
        type=int,
        default=10,
        help="Number of optimal routes to retrieve",
    )
    optimal_routes_parser.add_argument(
        "--ascending",
        action="store_true",
        help="Sort routes in ascending total duration order",
    )
    export_csv_parser = subparsers.add_parser(
        "export-csv", help="Export user walk data to a CSV file"
    )
    export_csv_parser.add_argument(
        "--user", type=str, required=True, help="User's name"
    )
    export_csv_parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output file path for the CSV.",
    )

    args = parser.parse_args()

    match args.command:
        case "init":
            initialize(args)
        case "fetch-hills":
            fetch_hills_data(args)
        case "fetch-walks":
            fetch_walks(args)
        case "reset-db":
            reset_database(args)
        case "add-user":
            add_user(args)
        case "directions":
            directions(args)
        case "walk-directions":
            get_walk_directions_for_user(args)
        case "optimal-routes":
            get_optimal_user_routes(args)
        case "export-csv":
            export_user_routes_to_csv(args)
        case _:
            logger.error("Unknown command")
            sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("--help")
    main()
