import logging
import time
import cloudscraper
from bs4 import BeautifulSoup
from typing import Any, Dict
import pandas as pd
from sports_data.core.interfaces import BaseExtractor
from sports_data.core.exceptions import ExtractionError, RateLimitError
from io import StringIO

import random

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux i686; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
]

class FBRefMatchLogExtractor(BaseExtractor):
    def __init__(self, delay: int = 3):
        self.delay = delay

    def get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }

    def extract(self, **kwargs: Any) -> Any:
        url = kwargs.get("url")
        if not url:
            raise ExtractionError("URL is required for extraction.")

        logger.info(f"Extracting from {url} with a delay of {self.delay}s to respect rate limits.")
        time.sleep(self.delay)

        headers = self.get_headers()
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, headers=headers)

        if response.status_code == 429:
            logger.error("Rate limit exceeded (HTTP 429).")
            raise RateLimitError("Rate limit exceeded on FBref.")
        elif response.status_code != 200:
            logger.error(f"Failed to fetch data, HTTP {response.status_code}.")
            raise ExtractionError(f"HTTP Error {response.status_code}")

        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'id': 'matchlogs_for'})

        if not table:
            logger.error("Could not find table with id 'matchlogs_for'")
            raise ExtractionError("Table 'matchlogs_for' not found in HTML.")

        try:
            # We use StringIO to wrap HTML string before passing to pd.read_html
            # to avoid pandas future warnings
            df = pd.read_html(StringIO(str(table)))[0]
            # When parsing multiline headers or single line headers, the structure might be a MultiIndex
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(0)

            # The data returned needs to be a list of dictionaries
            # and we need to pass along the URL to extract fbref_team_id and season later
            return {
                "url": url,
                "data": df.to_dict(orient="records")
            }
        except Exception as e:
            logger.error(f"Error parsing table into DataFrame: {e}")
            raise ExtractionError(f"Error parsing HTML table: {e}")
