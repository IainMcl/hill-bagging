from scraper.service import ScraperService
import pytest
from unittest.mock import MagicMock
from bs4 import BeautifulSoup
import httpx


class TestScraperService:
    @pytest.mark.parametrize(
        "url, expected",
        [
            (
                "https://www.walkhighlands.co.uk/munros/am-basteir",
                "https://www.walkhighlands.co.uk/munros/am-basteir",
            ),
            (
                "https://www.walkhighlands.co.uk/munros/am-basteir%20",
                "https://www.walkhighlands.co.uk/munros/am-basteir",
            ),
            (
                "https://www.walkhighlands.co.ukhttps://www.walkhighlands.co.uk/munros/am-basteir",
                "https://www.walkhighlands.co.uk/munros/am-basteir",
            ),
            (
                "http://www.walkhighlands.co.ukhttp://www.walkhighlands.co.uk/munros/am-basteir",
                "http://www.walkhighlands.co.uk/munros/am-basteir",
            ),
            (
                "https://www.walkhighlands.co.ukhttps://www.walkhighlands.co.uk/munros/am-basteir%20",
                "https://www.walkhighlands.co.uk/munros/am-basteir",
            ),
        ],
    )
    def test_sanitize_url(self, url: str, expected: str):
        assert ScraperService._sanitize_url(url) == expected

    def test_scrape_page_success(self, mocker):
        mock_response = MagicMock()
        mock_response.text = "<html><body><h1>Test</h1></body></html>"
        mock_response.raise_for_status.return_value = None
        mocker.patch("httpx.get", return_value=mock_response)

        result = ScraperService.scrape_page("http://example.com")

        assert "content" in result
        assert isinstance(result["content"], BeautifulSoup)
        assert result["content"].find("h1").text == "Test"

    def test_scrape_page_http_error(self, mocker):
        mocker.patch("httpx.get", side_effect=httpx.HTTPError("error"))

        result = ScraperService.scrape_page("http://example.com")

        assert result == {}
