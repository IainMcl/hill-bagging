from src.walkhighlands.api import WalkhighlandsAPI
import argparse
import sys


def initialize(args):
    print("Initializing with arguments:", args)
    WalkhighlandsAPI.initialize_app()


def fetch_munro_data(args):
    print("Fetching Munro data with arguments:", args)
    munros = WalkhighlandsAPI.get_munros()
    WalkhighlandsAPI.save_munros_to_db(munros)


def main():
    parser = argparse.ArgumentParser(
        description="Walkhighlands CLI Tool",
        usage="""
    main.py <command> [<args>]

    Commands:
        init: Initialize the application.
        fetch-munros: Fetch and store Munro data.
    """,
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True
    init_parser = subparsers.add_parser("init", help="Initialize the application")
    fetch_munros_parser = subparsers.add_parser(
        "fetch-munros", help="Fetch and store Munro data"
    )
    args = parser.parse_args()

    match args.command:
        case "init":
            initialize(args)
        case "fetch-munros":
            fetch_munro_data(args)
        case _:
            print("Unknown command")
            sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("--help")
    main()
