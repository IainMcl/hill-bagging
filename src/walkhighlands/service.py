import logging
import re
from bs4 import BeautifulSoup, Tag
from src.walkhighlands.dtos import HillPageData
from src.walkhighlands.dtos import WalkData, Walk
from src.walkhighlands.data.hill_data import WalkhighlandsData

logger = logging.getLogger(__name__)


class WalkhighlandsService:
    BASE_URL = "https://www.walkhighlands.co.uk"

    @classmethod
    def parse_munro_table_data(cls, bs_content: str) -> list[HillPageData]:
        """Parse HTML data to extract Munro table information."""

        munro_tables = bs_content.find_all("table", {"class": "table1"})  # type: ignore

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
                            mountain_url = f"{cls.BASE_URL}/munros/{relative_url}"
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

        logger.info(
            "Parsed Munros from all tables.", extra={"munro_count": len(mountain_data)}
        )
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
            logger.error(
                "Error parsing altitude",
                extra={"altitude_string": altitude, "error": e},
            )
            return None

    @classmethod
    def parse_walks_for_hill(cls, bs_content: str) -> list[Walk]:
        """Parse HTML content to extract walk URLs associated with a specific hill."""
        # 1. Find the target header element
        target_header: Tag | None = bs_content.find(  # type: ignore[arg-type]
            lambda tag: tag.name in ["h2", "h3"]  # type: ignore[arg-type]
            and "Detailed route description and map" in tag.get_text(strip=True)
        )

        if not target_header:
            # The header wasn't found
            return []

        walk_links = []
        for sibling in target_header.find_next_siblings():
            # Stop if we hit the next major section header
            if sibling.name in ["h2", "h3", "div"]:
                break

            # Check if the sibling is the <p> tag that contains the link
            if sibling.name == "p":
                # 3. Search INSIDE the <p> tag for the nested <a> tag
                link_tag: Tag | None = sibling.find("a")

                if link_tag and "href" in link_tag.attrs:
                    relative_url = link_tag["href"]

                    # 4. Construct the absolute URL
                    full_url = (
                        f"{cls.BASE_URL}{relative_url}"
                        if relative_url.startswith("/")
                        else relative_url
                    )

                    title = link_tag.get_text(strip=True) or "Walk Link"
                    walk_links.append(Walk(title=title, url=str(full_url)))

            # NOTE: A more robust parser might also check for the next section header
            # (e.g., 'Other routes and challenges') to stop the search, but
            # find_next_siblings('a') should generally stop once the next non-anchor
            # sibling appears, which is often sufficient on this site.

        return walk_links

    @classmethod
    def _get_hill_ids(cls, bs_content: BeautifulSoup) -> list[int]:
        """Extract hill IDs from the 'Summits Climbed' section of a walk page."""
        hill_ids: list[int] = []
        summits_header = bs_content.find(
            "h2", string=re.compile(r"\bSummits Climbed\b", re.IGNORECASE)
        )
        if not summits_header:
            logger.warning("Summits climbed header not found.")
            return hill_ids

        # Find the container for the summits climbed, which could be a 'dl' or 'div'
        summits_container = summits_header.find_next_sibling()
        if not summits_container:
            logger.warning("Summits climbed container not found.")
            return hill_ids

        # Find all links within the container
        summit_links = summits_container.find_all("a", href=True)
        for summit_link in summit_links:
            href = summit_link.get("href")
            if not href:
                continue

            if href.startswith("https://"):
                mountain_url = href
            else:
                mountain_url = f"{cls.BASE_URL}{href}"

            hill_id = WalkhighlandsData.get_hill_id_by_url(mountain_url)
            if hill_id is not None:
                hill_ids.append(hill_id)
        return hill_ids

    @classmethod
    def parse_walk_data(cls, bs_content: str, walk_url: str) -> WalkData | None:
        """Parse HTML content to extract detailed walk data."""
        # Implementation would go here
        title_tag = bs_content.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else "Unknown Walk"  # type: ignore

        # Locate the container that holds all the statistics
        stats_header = bs_content.find(  # type: ignore
            "h2", string=re.compile(r"\bWalk Statistics\b", re.IGNORECASE)
        )
        if not stats_header:
            logger.warning("Walk statistics header not found.")
            return None
        stats_container = stats_header.find_next_sibling("dl")  # type: ignore
        if not stats_container:
            logger.warning("Walk statistics container not found.")
            return None

        # Helper function to safely extract text data from a specific statistic
        def get_stat_value(text_label: str) -> str:
            label_tag = stats_container.find(  # type: ignore
                "dt",
                string=re.compile(r"\b" + re.escape(text_label) + r"\b", re.IGNORECASE),
            )
            value = label_tag.find_next_sibling("dd")  # type: ignore
            return value.get_text(strip=True) if value else ""

        distance_str = get_stat_value("Distance")
        ascent_str = get_stat_value("Ascent")
        duration_str = get_stat_value("Time")
        grid_ref_str = get_stat_value("Start Grid Ref")

        # --- 2. Grade and Bog Factor (Count icons) ---
        grade_int = len(bs_content.find_all("div", class_=re.compile(r"\bgrade\b")))  # type: ignore
        bog_factor_int = len(
            bs_content.find_all("div", class_=re.compile(r"\bbog\sfactor\b"))  # type: ignore
        )

        # --- 3. User Rating (Extract value before /5) ---
        rating_tag = bs_content.find("strong", string="Rating")  # type: ignore
        rating_value = 0.0
        if rating_tag and rating_tag.next_sibling:  # type: ignore[attr-defined]
            try:
                rating_text = rating_tag.next_sibling.strip().split("/")[0]  # type: ignore[attr-defined]
                rating_value = float(rating_text)
            except Exception:
                pass

        # --- 4. Hill IDs  ---
        hill_ids = cls._get_hill_ids(bs_content)

        # --- 5. Parsing and Conversion (Robustness check) ---

        try:
            distance_km = float(re.search(r"([\d\.]+)\s*km", distance_str).group(1))  # type: ignore
        except Exception:
            distance_km = 0.0

        try:
            ascent_m = int(re.search(r"(\d+)\s*m", ascent_str).group(1))  # type: ignore
        except Exception:
            ascent_m = 0

        try:
            times = re.findall(r"(\d+)", duration_str)
            if len(times) >= 2:
                # Be presumptuous and always take the smallest time
                duration_hr = float(times[0])
            elif len(times) == 1:
                duration_hr = float(times[0])
            else:
                duration_hr = 0.0
        except Exception:
            duration_hr = 0.0

        # --- 6. Start Location ---
        # Find string 'open in google maps'
        start_location = ""
        maps_link = bs_content.find(  # type: ignore[call-arg]
            "a",
            string=re.compile(r"\bopen in google maps\b", re.IGNORECASE),
        )
        if maps_link:  # type: ignore[attr-defined]
            start_location = maps_link.get("href", "")  # type: ignore[attr-defined]

        try:
            walk_data_model = WalkData(
                title=title,
                url=walk_url or "",
                distance_km=distance_km,
                ascent_m=ascent_m,
                duration_hr=duration_hr,
                bog_factor=bog_factor_int,
                user_rating=rating_value,
                start_grid_ref=grid_ref_str,
                grade=grade_int,
                start_location=start_location or "",
                hill_ids=hill_ids,
            )
            return walk_data_model
        except Exception:
            logger.exception("Error creating WalkData model")
            return None
