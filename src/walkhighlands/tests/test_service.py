from walkhighlands.service import WalkhighlandsService
from walkhighlands.dtos import HillPageData, Walk, WalkData
import pytest
from bs4 import BeautifulSoup
from unittest.mock import patch


class TestWalkhighlandsService:
    @pytest.mark.parametrize(
        "altitude_str, expected_meters",
        [
            ("123m", 123),
            ("328ft", 99),
            ("456", 456),
            ("  600m  ", 600),
            (" 1000 ft ", 304),
        ],
    )
    def test_parse_altitude_string_valid(self, altitude_str, expected_meters):
        assert (
            WalkhighlandsService._parse_altitude_string(altitude_str) == expected_meters
        )

    def test_parse_altitude_string_invalid(self):
        assert WalkhighlandsService._parse_altitude_string("abc") is None

    def test_parse_munro_table_data_success(self):
        with open("src/walkhighlands/tests/test_data/munro_table.html", "r") as f:
            html_content = f.read()
        result = WalkhighlandsService.parse_munro_table_data(html_content)

        expected = [
            HillPageData(
                url="https://www.walkhighlands.co.uk/munros/ben-nevis",
                name="Ben Nevis",
                region="Fort William",
                altitude=1345,
            ),
            HillPageData(
                url="https://www.walkhighlands.co.uk/munros/ben-macdui",
                name="Ben Macdui",
                region="Cairngorms",
                altitude=1309,
            ),
        ]
        assert [item.model_dump() for item in result] == [
            item.model_dump() for item in expected
        ]

    def test_parse_munro_table_data_empty_html(self):
        result = WalkhighlandsService.parse_munro_table_data("")
        assert result == []

    def test_parse_munro_table_data_no_munro_tables(self):
        html_content = "<html><body><p>No tables here</p></body></html>"
        result = WalkhighlandsService.parse_munro_table_data(html_content)
        assert result == []

    def test_parse_munro_table_data_no_tbody(self):
        html_content = '<html><body><table class="table1"><thead><tr><th>Header</th></tr></thead></table></body></html>'
        result = WalkhighlandsService.parse_munro_table_data(html_content)
        assert result == []

    def test_parse_munro_table_data_no_anchor_tag(self):
        html_content = '<html><body><table class="table1"><tbody><tr><td>No Link</td><td>Region</td><td>1000m</td></tr></tbody></table></body></html>'
        result = WalkhighlandsService.parse_munro_table_data(html_content)
        assert result == []

    def test_parse_walks_for_hill_success(self):
        with open("src/walkhighlands/tests/test_data/hill_page_walks.html", "r") as f:
            html_content = f.read()
        result = WalkhighlandsService.parse_walks_for_hill(html_content)

        expected = [
            Walk(
                title="Walk 1 Title", url="https://www.walkhighlands.co.uk/walks/walk1"
            ),
            Walk(
                title="Walk 2 Title", url="https://www.walkhighlands.co.uk/walks/walk2"
            ),
        ]
        assert [item.model_dump() for item in result] == [
            item.model_dump() for item in expected
        ]

    def test_parse_walks_for_hill_no_target_header(self):
        html_content = "<html><body><p>Some content</p></body></html>"
        result = WalkhighlandsService.parse_walks_for_hill(html_content)
        assert result == []

    def test_parse_walks_for_hill_no_walk_links(self):
        html_content = "<html><body><h2>Detailed route description and map</h2><p>No links here</p></body></html>"
        result = WalkhighlandsService.parse_walks_for_hill(html_content)
        assert result == []

    @patch("walkhighlands.service.WalkhighlandsData.get_hill_id_by_url")
    def test_get_hill_ids_success(self, mock_get_hill_id_by_url):
        mock_get_hill_id_by_url.side_effect = [
            1,  # For https://www.walkhighlands.co.uk/munros/ben-nevis
            2,  # For https://www.walkhighlands.co.uk/munros/ben-macdui
        ]
        with open("src/walkhighlands/tests/test_data/walk_page_summits.html", "r") as f:
            html_content = f.read()
        bs_content = BeautifulSoup(html_content, "html.parser")
        result = WalkhighlandsService._get_hill_ids(bs_content)

        assert result == [1, 2]
        mock_get_hill_id_by_url.assert_any_call(
            "https://www.walkhighlands.co.uk/munros/ben-nevis"
        )
        mock_get_hill_id_by_url.assert_any_call(
            "https://www.walkhighlands.co.uk/munros/ben-macdui"
        )

    def test_get_hill_ids_no_summits_header(self):
        html_content = "<html><body><p>No summits here</p></body></html>"
        bs_content = BeautifulSoup(html_content, "html.parser")
        result = WalkhighlandsService._get_hill_ids(bs_content)
        assert result == []

    def test_get_hill_ids_no_summits_container(self):
        html_content = (
            "<html><body><h2>Summits Climbed</h2><p>No container</p></body></html>"
        )
        bs_content = BeautifulSoup(html_content, "html.parser")
        result = WalkhighlandsService._get_hill_ids(bs_content)
        assert result == []

    def test_get_hill_ids_no_links(self):
        html_content = "<html><body><h2>Summits Climbed</h2><dl><dt>No links</dt></dl></body></html>"
        bs_content = BeautifulSoup(html_content, "html.parser")
        result = WalkhighlandsService._get_hill_ids(bs_content)
        assert result == []

    @patch("walkhighlands.service.WalkhighlandsService._get_hill_ids")
    def test_parse_walk_data_success(self, mock_get_hill_ids):
        mock_get_hill_ids.return_value = [1]
        with open("src/walkhighlands/tests/test_data/walk_data_page.html", "r") as f:
            html_content = f.read()
        walk_url = "https://www.walkhighlands.co.uk/fort-william/ben-nevis.shtml"
        result = WalkhighlandsService.parse_walk_data(html_content, walk_url)

        expected = WalkData(
            title="Ben Nevis via the Mountain Track",
            url="https://www.walkhighlands.co.uk/fort-william/ben-nevis.shtml",
            distance_km=17.0,
            ascent_m=1352,
            duration_hr=7.0,
            bog_factor=3,
            user_rating=4.5,
            start_grid_ref="NN123723",
            grade=2,
            start_location="https://www.google.com/maps?q=NN123723",
            hill_ids=[1],
        )
        assert result.model_dump() == expected.model_dump()

    @patch("walkhighlands.service.WalkhighlandsService._get_hill_ids")
    def test_parse_walk_data_no_walk_statistics_header(self, mock_get_hill_ids):
        html_content = "<html><body><h1>Title</h1><p>No stats</p></body></html>"
        walk_url = "https://www.walkhighlands.co.uk/fort-william/ben-nevis.shtml"
        result = WalkhighlandsService.parse_walk_data(html_content, walk_url)
        assert result is None

    @patch("walkhighlands.service.WalkhighlandsService._get_hill_ids")
    def test_parse_walk_data_no_walk_statistics_container(self, mock_get_hill_ids):
        html_content = "<html><body><h1>Title</h1><h2>Walk Statistics</h2><p>No container</p></body></html>"
        walk_url = "https://www.walkhighlands.co.uk/fort-william/ben-nevis.shtml"
        result = WalkhighlandsService.parse_walk_data(html_content, walk_url)
        assert result is None

    @patch("walkhighlands.service.WalkhighlandsService._get_hill_ids")
    def test_parse_walk_data_missing_data_points(self, mock_get_hill_ids):
        mock_get_hill_ids.return_value = []
        html_content = (
            "<html><body><h1>Title</h1><h2>Walk Statistics</h2><dl></dl></body></html>"
        )
        walk_url = "https://www.walkhighlands.co.uk/fort-william/ben-nevis.shtml"
        result = WalkhighlandsService.parse_walk_data(html_content, walk_url)

        expected = WalkData(
            title="Title",
            url="https://www.walkhighlands.co.uk/fort-william/ben-nevis.shtml",
            distance_km=0.0,
            ascent_m=0,
            duration_hr=0.0,
            bog_factor=0,
            user_rating=0.0,
            start_grid_ref="",
            grade=0,
            start_location="",
            hill_ids=[],
        )
        assert result.model_dump() == expected.model_dump()
