from unittest.mock import patch
from walkhighlands.api import WalkhighlandsAPI
from walkhighlands.dtos import HillPageData, Walk, WalkData
from bs4 import BeautifulSoup


class TestWalkhighlandsAPI:
    @patch("walkhighlands.api.ScraperAPI.fetch_data")
    @patch("walkhighlands.api.WalkhighlandsService.parse_munro_table_data")
    def test_get_munros_success(self, mock_parse_munro_table_data, mock_fetch_data):
        mock_fetch_data.return_value = {
            "content": BeautifulSoup("<html></html>", "html.parser")
        }
        mock_parse_munro_table_data.return_value = [
            HillPageData(url="url1", name="Munro 1", region="Region 1", altitude=1000)
        ]

        result = WalkhighlandsAPI.get_munros()

        mock_fetch_data.assert_called_once_with(
            "https://www.walkhighlands.co.uk/munros/munros-a-z"
        )
        mock_parse_munro_table_data.assert_called_once()
        assert len(result) == 1
        assert result[0].name == "Munro 1"

    @patch("walkhighlands.api.ScraperAPI.fetch_data")
    @patch("walkhighlands.api.WalkhighlandsService.parse_munro_table_data")
    def test_get_munros_no_content(self, mock_parse_munro_table_data, mock_fetch_data):
        mock_fetch_data.return_value = {"content": ""}

        result = WalkhighlandsAPI.get_munros()

        mock_fetch_data.assert_called_once_with(
            "https://www.walkhighlands.co.uk/munros/munros-a-z"
        )
        mock_parse_munro_table_data.assert_not_called()
        assert result == []

    @patch("walkhighlands.api.WalkhighlandsData.save_hill_data")
    def test_save_munros_success(self, mock_save_hill_data):
        munros = [
            HillPageData(url="url1", name="Munro 1", region="Region 1", altitude=1000),
            HillPageData(url="url2", name="Munro 2", region="Region 2", altitude=2000),
        ]
        WalkhighlandsAPI.save_munros(munros)

        assert mock_save_hill_data.call_count == 2
        mock_save_hill_data.assert_any_call(munros[0])
        mock_save_hill_data.assert_any_call(munros[1])

    @patch("walkhighlands.api.WalkhighlandsData.save_hill_data")
    def test_save_munros_empty_list(self, mock_save_hill_data):
        munros = []
        WalkhighlandsAPI.save_munros(munros)

        mock_save_hill_data.assert_not_called()

    @patch("walkhighlands.api.ScraperAPI.fetch_data")
    @patch("walkhighlands.api.WalkhighlandsService.parse_walks_for_hill")
    def test_get_walks_for_hill_success(
        self, mock_parse_walks_for_hill, mock_fetch_data
    ):
        hill_url = "https://www.walkhighlands.co.uk/munros/ben-nevis"
        mock_fetch_data.return_value = {
            "content": BeautifulSoup("<html></html>", "html.parser")
        }
        mock_parse_walks_for_hill.return_value = [
            Walk(title="Walk 1", url="url1"),
            Walk(title="Walk 2", url="url2"),
        ]

        result = WalkhighlandsAPI.get_walks_for_hill(hill_url)

        mock_fetch_data.assert_called_once_with(hill_url)
        mock_parse_walks_for_hill.assert_called_once_with(
            mock_fetch_data.return_value["content"]
        )
        assert len(result) == 2
        assert result[0].title == "Walk 1"

    @patch("walkhighlands.api.ScraperAPI.fetch_data")
    @patch("walkhighlands.api.WalkhighlandsService.parse_walks_for_hill")
    def test_get_walks_for_hill_no_content(
        self, mock_parse_walks_for_hill, mock_fetch_data
    ):
        hill_url = "https://www.walkhighlands.co.uk/munros/ben-nevis"
        mock_fetch_data.return_value = {"content": ""}

        result = WalkhighlandsAPI.get_walks_for_hill(hill_url)

        mock_fetch_data.assert_called_once_with(hill_url)
        mock_parse_walks_for_hill.assert_not_called()
        assert result == []

    @patch("walkhighlands.api.ScraperAPI.fetch_data")
    @patch("walkhighlands.api.WalkhighlandsService.parse_walk_data")
    def test_get_walk_data_success(self, mock_parse_walk_data, mock_fetch_data):
        walk_url = "https://www.walkhighlands.co.uk/walks/walk1"
        mock_fetch_data.return_value = {
            "content": BeautifulSoup("<html></html>", "html.parser")
        }
        mock_parse_walk_data.return_value = WalkData(
            title="Walk 1",
            url="url1",
            distance_km=10.0,
            ascent_m=500,
            duration_hr=3.0,
            bog_factor=1,
            user_rating=4.0,
            start_grid_ref="NN123456",
            grade=1,
            start_location="start_loc",
            hill_ids=[1, 2],
        )

        result = WalkhighlandsAPI.get_walk_data(walk_url)

        mock_fetch_data.assert_called_once_with(walk_url)
        mock_parse_walk_data.assert_called_once_with(
            mock_fetch_data.return_value["content"], walk_url
        )
        assert result.title == "Walk 1"

    @patch("walkhighlands.api.ScraperAPI.fetch_data")
    @patch("walkhighlands.api.WalkhighlandsService.parse_walk_data")
    def test_get_walk_data_no_content(self, mock_parse_walk_data, mock_fetch_data):
        walk_url = "https://www.walkhighlands.co.uk/walks/walk1"
        mock_fetch_data.return_value = {"content": ""}

        result = WalkhighlandsAPI.get_walk_data(walk_url)

        mock_fetch_data.assert_called_once_with(walk_url)
        mock_parse_walk_data.assert_not_called()
        assert result is None

    @patch("walkhighlands.api.WalkhighlandsData.fetch_all_hill_urls")
    def test_get_hill_urls_success(self, mock_fetch_all_hill_urls):
        mock_fetch_all_hill_urls.return_value = ["url1", "url2"]

        result = WalkhighlandsAPI.get_hill_urls()

        mock_fetch_all_hill_urls.assert_called_once()
        assert result == ["url1", "url2"]

    @patch("walkhighlands.api.WalkhighlandsData.fetch_all_hill_urls")
    def test_get_hill_urls_no_urls(self, mock_fetch_all_hill_urls):
        mock_fetch_all_hill_urls.return_value = []

        result = WalkhighlandsAPI.get_hill_urls()

        mock_fetch_all_hill_urls.assert_called_once()
        assert result == []

    @patch("walkhighlands.api.WalkhighlandsData.insert_walk")
    def test_save_walk_success(self, mock_insert_walk):
        walk_data = WalkData(
            title="Walk 1",
            url="url1",
            distance_km=10.0,
            ascent_m=500,
            duration_hr=3.0,
            bog_factor=1,
            user_rating=4.0,
            start_grid_ref="NN123456",
            grade=1,
            start_location="start_loc",
            hill_ids=[1, 2],
        )
        WalkhighlandsAPI.save_walk(walk_data)

        mock_insert_walk.assert_called_once_with(walk_data)

    @patch("walkhighlands.api.WalkhighlandsData.create_hill_data_table")
    @patch("walkhighlands.api.WalkhighlandsData.create_walk_data_table")
    @patch("walkhighlands.api.WalkhighlandsData.create_walk_hill_decomp_table")
    def test_initialize_app_success(
        self,
        mock_create_walk_hill_decomp_table,
        mock_create_walk_data_table,
        mock_create_hill_data_table,
    ):
        WalkhighlandsAPI.initialize_app()

        mock_create_hill_data_table.assert_called_once()
        mock_create_walk_data_table.assert_called_once()
        mock_create_walk_hill_decomp_table.assert_called_once()

    @patch("walkhighlands.api.WalkhighlandsData.reset_database")
    def test_reset_database_no_tables(self, mock_reset_database):
        WalkhighlandsAPI.reset_database()

        mock_reset_database.assert_called_once_with(None)

    @patch("walkhighlands.api.WalkhighlandsData.reset_database")
    def test_reset_database_with_tables(self, mock_reset_database):
        tables = ["hills", "walks"]
        WalkhighlandsAPI.reset_database(tables)

        mock_reset_database.assert_called_once_with(tables)
