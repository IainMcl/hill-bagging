from src.walkhighlands.api import WalkhighlandsAPI
from src.users.api import UsersAPI
import argparse
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize(args):
    logger.info("Initializing with arguments", extra={"args": args})
    WalkhighlandsAPI.initialize_app()
<<<<<<< Updated upstream
    logger.info("Initialization complete.")
=======
    UsersAPI.initialize_users()
>>>>>>> Stashed changes


def fetch_hills_data(args):
    logger.info("Fetching Munro data with arguments", extra={"args": args})
    munros = WalkhighlandsAPI.get_munros()
    WalkhighlandsAPI.save_munros(munros)


def fetch_walks(args):
    logger.info("Fetching walks with arguments", extra={"args": args})
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
    logger.info("Resetting database with arguments", extra={"args": args})
    WalkhighlandsAPI.reset_database(args.tables)
    logger.info("Database reset complete.")


def add_user(args):
    UsersAPI.add_user(args.name, args.location)


def main():
    parser = argparse.ArgumentParser(
        description="Walkhighlands CLI Tool",
        usage="""
    main.py <command> [<args>]

    Commands:
        init: Initialize the application.
<<<<<<< Updated upstream
        fetch-hills: Fetch and store Munro data.
        fetch-walks: Fetch walks for a specific hill.
        reset-db: Reset the database.
=======
        fetch-munros: Fetch and store Munro data.
        add-user: Add a new user.
>>>>>>> Stashed changes
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
    args = parser.parse_args()

    match args.command:
        case "init":
            initialize(args)
<<<<<<< Updated upstream
        case "fetch-hills":
            fetch_hills_data(args)
        case "fetch-walks":
            fetch_walks(args)
        case "reset-db":
            reset_database(args)
=======
        case "fetch-munros":
            fetch_munro_data(args)
        case "add-user":
            add_user(args)
>>>>>>> Stashed changes
        case _:
            logger.error("Unknown command")
            sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("--help")
    main()
