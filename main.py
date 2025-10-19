from src.walkhighlands.api import WalkhighlandsAPI
import argparse
import sys
import time
import logging

logger = logging.getLogger(__name__)


def initialize(args):
    logger.info("Initializing with arguments:", args)
    WalkhighlandsAPI.initialize_app()
    logger.info("Initialization complete.")


def fetch_munro_data(args):
    logger.info("Fetching Munro data with arguments:", args)
    munros = WalkhighlandsAPI.get_munros()
    WalkhighlandsAPI.save_munros(munros)


def fetch_walks(args):
    logger.info("Fetching walks with arguments:", args)
    hill_urls = WalkhighlandsAPI.get_hill_urls()
    # hill_urls = ["https://www.walkhighlands.co.uk/munros/creag-a-mhaim"]
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


def main():
    parser = argparse.ArgumentParser(
        description="Walkhighlands CLI Tool",
        usage="""
    main.py <command> [<args>]

    Commands:
        init: Initialize the application.
        fetch-hills: Fetch and store Munro data.
        fetch-walks: Fetch walks for a specific hill.
    """,
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True
    init_parser = subparsers.add_parser("init", help="Initialize the application")
    fetch_hill_parser = subparsers.add_parser(
        "fetch-munros", help="Fetch and store Munro data"
    )
    fetch_walks_parser = subparsers.add_parser(
        "fetch-walks", help="Fetch walks for a specific hill"
    )
    args = parser.parse_args()

    match args.command:
        case "init":
            initialize(args)
        case "fetch-hills":
            fetch_munro_data(args)
        case "fetch-walks":
            fetch_walks(args)
        case _:
            logger.error("Unknown command")
            sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("--help")
    main()
