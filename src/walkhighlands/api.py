from src.scraper.api import ScraperAPI
from src.database.api import DatabaseAPI
from src.walkhighlands.dtos import HillPageData
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
    def save_munros_to_db(munros: list[HillPageData]) -> None:
        """Save Munros data to the database."""
        for munro in munros:
            WalkhighlandsData.save_hill_data(munro)

    @staticmethod
    def initialize_app() -> None:
        """Initialize the Walkhighlands application."""
        WalkhighlandsData.create_hill_data_table()
