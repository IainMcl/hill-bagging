import logging
from bs4 import BeautifulSoup
from src.walkhighlands.dtos import HillPageData

logger = logging.getLogger(__name__)


class WalkhighlandsService:
    BASE_URL = "https://www.walkhighlands.co.uk/munros/"

    @classmethod
    def parse_munro_table_data(cls, bs_content: str) -> list[HillPageData]:
        """Parse HTML data to extract Munro table information."""

        munro_tables = bs_content.find_all("table", {"class": "table1"})

        if not munro_tables:
            logger.warning("Munro tables not found in the provided HTML data.")
            return []

        mountain_data = []

        for munro_table in munro_tables:
            # Now, call find_all("tbody") on the SINGLE, current table (munro_table)
            bodys = munro_table.find_all("tbody")

            if not bodys:
                logger.warning("No table body found in a Munro table.")
                continue

            # 3. Continue your original iteration logic
            for table_body in bodys:
                rows = table_body.find_all("tr")
                for row in rows:
                    columns = row.find_all("td")

                    if len(columns) == 3:
                        anchor_tag = columns[0].find("a")

                        # Check if an anchor tag exists
                        if not anchor_tag:
                            logger.warning(
                                "Mountain anchor tag not found for a row; skipping."
                            )
                            continue

                        relative_url = anchor_tag.get("href")

                        if relative_url:
                            # Prepend the base URL to create the full, absolute URL
                            # Assuming BASE_URL is accessible here, e.g., WalkhighlandsService.BASE_URL
                            mountain_url = f"{cls.BASE_URL}{relative_url}"
                        else:
                            logger.warning(
                                "Mountain URL (href) not found for a row; skipping."
                            )
                            continue
                        mountain_name_tag = columns[0].find("a")
                        mountain_name = (
                            mountain_name_tag.get_text(strip=True)
                            if mountain_name_tag
                            else columns[0].get_text(strip=True)
                        )
                        region = columns[1].get_text(strip=True)
                        altitude = columns[2].get_text(strip=True)
                        alt = WalkhighlandsService._parse_altitude_string(altitude)

                        mountain_data.append(
                            HillPageData(
                                url=mountain_url,
                                name=mountain_name,
                                region=region,
                                altitude=alt or 0,
                            )
                        )

        logger.info(f"Parsed {len(mountain_data)} Munros from all tables.")
        return mountain_data

    @staticmethod
    def _parse_altitude_string(altitude: str) -> int | None:
        """Convert altitude string to an integer value in meters."""
        try:
            if "m" in altitude:
                return int(altitude.replace("m", "").strip())
            elif "ft" in altitude:
                feet = int(altitude.replace("ft", "").strip())
                return int(feet * 0.3048)  # Convert feet to meters
            else:
                return int(altitude.strip())
        except ValueError as e:
            logger.error(f"Error parsing altitude '{altitude}': {e}")
            return None
