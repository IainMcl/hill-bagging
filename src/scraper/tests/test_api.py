from scraper.api import ScraperAPI
from unittest.mock import patch


def test_fetch_data():
    with patch("scraper.api.ScraperService.scrape_page") as mock_scrape_page:
        mock_scrape_page.return_value = {"content": "test"}
        result = ScraperAPI.fetch_data("http://example.com")
        mock_scrape_page.assert_called_once_with("http://example.com")
        assert result == {"content": "test"}
