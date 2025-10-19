from bs4 import BeautifulSoup
import httpx


class ScraperService:
    @staticmethod
    def scrape_page(url: str) -> dict[str, BeautifulSoup]:
        """Scrape data from a given webpage URL."""
        try:
            response = httpx.get(url)
            response.raise_for_status()
            return {"content": BeautifulSoup(response.text, "html.parser")}
        except httpx.HTTPError as e:
            print(f"An error occurred while scraping the page: {e}")
            return {}
