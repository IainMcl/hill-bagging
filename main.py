from src.walkhighlands.api import WalkhighlandsAPI
import argparse
import sys
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize(args):
    logger.info("Initializing with arguments:", args)
    WalkhighlandsAPI.initialize_app()
    logger.info("Initialization complete.")


def fetch_hills_data(args):
    logger.info("Fetching Munro data with arguments:", args)
    munros = WalkhighlandsAPI.get_munros()
    WalkhighlandsAPI.save_munros(munros)


def fetch_walks(args):
    logger.info("Fetching walks with arguments:", args)
    hill_urls = WalkhighlandsAPI.get_hill_urls()
    for hill_url in hill_urls:
        walks = WalkhighlandsAPI.get_walks_for_hill(hill_url)
        for walk in walks:
            walk_data = WalkhighlandsAPI.get_walk_data(walk.url)
            # save
            if walk_data:
                WalkhighlandsAPI.save_walk(walk_data)
            else:
                logger.error(f"Failed to fetch walk data for {walk.url}")
        # time.sleep(1)  # Be polite and avoid overwhelming the server


def fetch_gpx_for_walk(args):
    walk_id = args.walk_id
    logger.info(f"Fetching GPX data for walk ID: {walk_id}")
    gpx_data = WalkhighlandsAPI.get_gpx_for_walk(walk_id=walk_id)
    logger.info(f"GPX data fetched for walk ID {walk_id}: {gpx_data is not None}")
    if gpx_data:
        # WalkhighlandsAPI.save_gpx_data(walk_id, gpx_data)
        logger.info(f"GPX data for walk ID {walk_id} saved successfully.")
    else:
        logger.error(f"Failed to fetch GPX data for walk ID {walk_id}")


def reset_database(args):
    logger.info("Resetting database with arguments:", args)
    WalkhighlandsAPI.reset_database(args.tables)
    logger.info("Database reset complete.")


def main():
    parser = argparse.ArgumentParser(
        description="Walkhighlands CLI Tool",
        usage="""
    main.py <command> [<args>]

    Commands:
        init: Initialize the application.
        fetch-hills: Fetch and store Munro data.
        fetch-walks: Fetch walks for a specific hill.
        fetch-gpx: Fetch GPX data for a specific walk.
        reset-db: Reset the database.
    """,
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True
    init_parser = subparsers.add_parser("init", help="Initialize the application")
    fetch_hill_parser = subparsers.add_parser(
        "fetch-hills", help="Fetch and store Munro data"
    )
    fetch_walks_parser = subparsers.add_parser(
        "fetch-walks", help="Fetch walks for a specific hill"
    )
    fetch_gpx_parser = subparsers.add_parser(
        "fetch-gpx", help="Fetch GPX data for a specific walk"
    )
    fetch_gpx_parser.add_argument(
        "--walk-id",
        type=int,
        required=True,
        help="ID of the walk to fetch GPX data for",
    )
    reset_db_parser = subparsers.add_parser("reset-db", help="Reset the database")
    reset_db_parser.add_argument(
        "--tables",
        nargs="+",
        choices=["hills", "walks", "walk_hill_decomposition"],
        help="Specify which tables to reset.",
    )
    args = parser.parse_args()

    match args.command:
        case "init":
            initialize(args)
        case "fetch-hills":
            fetch_hills_data(args)
        case "fetch-walks":
            fetch_walks(args)
        case "fetch-gpx":
            fetch_gpx_for_walk(args)
        case "reset-db":
            reset_database(args)
        case _:
            logger.error("Unknown command")
            sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("--help")
    main()
