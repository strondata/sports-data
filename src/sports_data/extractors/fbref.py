import logging
import time
import requests
from bs4 import BeautifulSoup
from typing import Any, List, Dict
import pandas as pd
from sports_data.core.interfaces import BaseExtractor
from sports_data.core.exceptions import ExtractionError, RateLimitError
from io import StringIO

logger = logging.getLogger(__name__)

class FBRefMatchLogExtractor(BaseExtractor):
    def __init__(self, delay: int = 3):
        self.delay = delay
        self.headers = {
            "User-Agent": "sports-data-etl/1.0 (Contact: user@example.com)"
        }

    def extract(self, **kwargs: Any) -> Any:
        url = kwargs.get("url")
        if not url:
            raise ExtractionError("URL is required for extraction.")

        logger.info(f"Extracting from {url} with a delay of {self.delay}s to respect rate limits.")
        time.sleep(self.delay)

        response = requests.get(url, headers=self.headers)

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
