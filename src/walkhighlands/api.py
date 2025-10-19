from src.scraper.api import ScraperAPI
from src.database.api import DatabaseAPI
from src.walkhighlands.dtos import HillPageData, Walk, WalkData
from src.walkhighlands.service import WalkhighlandsService
from src.walkhighlands.data.hill_data import WalkhighlandsData
import logging

logger = logging.getLogger(__name__)


class WalkhighlandsAPI:
    @staticmethod
    def get_munros() -> list[HillPageData]:
        """Fetch Munros data from Walkhighlands."""
        url = "https://www.walkhighlands.co.uk/munros/munros-a-z"
        data = ScraperAPI.fetch_data(url)
        content = data.get("content", "")
        if not content:
            logger.error("No content fetched from the Walkhighlands page.")
            return []
        return WalkhighlandsService.parse_munro_table_data(content)

    @staticmethod
    def save_munros(munros: list[HillPageData]) -> None:
        """Save Munros data to the database."""
        for munro in munros:
            WalkhighlandsData.save_hill_data(munro)

    @staticmethod
    def get_walks_for_hill(hill_url: str) -> list[Walk]:
        """Fetch walks associated with a specific hill."""
        hill_data = ScraperAPI.fetch_data(hill_url)
        content = hill_data.get("content", "")
        if not content:
            logger.error(f"No content fetched from the hill page: {hill_url}")
            return []
        return WalkhighlandsService.parse_walks_for_hill(content)

    @staticmethod
    def get_walk_data(walk_url: str) -> WalkData | None:
        """Fetch detailed walk data from a walk URL."""
        walk_data = ScraperAPI.fetch_data(walk_url)
        content = walk_data.get("content", "")
        if not content:
            logger.error(f"No content fetched from the walk page: {walk_url}")
            return None
        return WalkhighlandsService.parse_walk_data(content, walk_url)

    @staticmethod
    def get_hill_urls() -> list[str]:
        """Retrieve all hill URLs from the database."""
        return WalkhighlandsData.fetch_all_hill_urls()

    @staticmethod
    def save_walk(walk_data: WalkData) -> None:
        """Save walk data to the database."""
        WalkhighlandsData.insert_walk(walk_data)

    @staticmethod
    def initialize_app() -> None:
        """Initialize the Walkhighlands application."""
        WalkhighlandsData.create_hill_data_table()
        WalkhighlandsData.create_walk_data_table()
        WalkhighlandsData.create_walk_hill_decomp_table()
