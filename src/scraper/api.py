from src.scraper.service import ScraperService


class ScraperAPI:
    @staticmethod
    def fetch_data(url: str) -> dict:
        """Fetch data from a given source URL."""
        return ScraperService.scrape_page(url)
