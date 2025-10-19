from bs4 import BeautifulSoup
import httpx


class ScraperService:
    @staticmethod
    def scrape_page(url: str) -> dict[str, BeautifulSoup]:
        """Scrape data from a given webpage URL."""
        try:
            print(f"Scraping URL: {url}")
            sanitized_url = ScraperService._sanitize_url(url)
            response = httpx.get(sanitized_url)
            response.raise_for_status()
            return {"content": BeautifulSoup(response.text, "html.parser")}
        except httpx.HTTPError as e:
            print(f"An error occurred while scraping the page: {e}")
            return {}

    @staticmethod
    def _sanitize_url(url: str) -> str:
        """
        Sanitize the URL to ensure it's well-formed.
        Some contain '%20' at the end
        some incorrectly formed urls https://www.walkhighlands.co.ukhttp://www.walkhighlands.co.uk/munros/am-basteir
        """
        # check for '%20' at the end
        if url.endswith("%20"):
            url = url[:-3]
        # check for duplicated domain
        # only handle until the second occurance of https:// or http://
        if url.count("https://") > 1:
            parts = url.split("https://")
            url = "https://" + parts[-1]
        elif url.count("http://") > 1:
            parts = url.split("http://")
            url = "http://" + parts[-1]
        return url
