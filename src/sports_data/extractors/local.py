import logging
from bs4 import BeautifulSoup
from typing import Any
import pandas as pd
from sports_data.core.interfaces import BaseExtractor
from sports_data.core.exceptions import ExtractionError
from io import StringIO
from pathlib import Path

logger = logging.getLogger(__name__)

class LocalFBRefExtractor(BaseExtractor):
    def __init__(self, file_path: str = "data/raw_samples/bayern_mock.html"):
        self.file_path = file_path

    def extract(self, **kwargs: Any) -> Any:
        # Default mock url since we aren't fetching a real one, but the transformer needs it
        url = kwargs.get("url", "https://fbref.com/en/squads/054efa67/2025-2026/matchlogs/all_comps/schedule/Bayern-Munich-Scores-and-Fixtures-All-Competitions")

        path = Path(self.file_path)
        if not path.exists():
            raise ExtractionError(f"Local file not found: {self.file_path}")

        logger.info(f"Extracting data from local file: {self.file_path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            raise ExtractionError(f"Error reading local file: {e}")

        soup = BeautifulSoup(content, 'html.parser')
        table = soup.find('table', {'id': 'matchlogs_for'})

        if not table:
            logger.error("Could not find table with id 'matchlogs_for'")
            raise ExtractionError("Table 'matchlogs_for' not found in HTML.")

        try:
            df = pd.read_html(StringIO(str(table)))[0]
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(0)

            return {
                "url": url,
                "data": df.to_dict(orient="records")
            }
        except Exception as e:
            logger.error(f"Error parsing table into DataFrame: {e}")
            raise ExtractionError(f"Error parsing HTML table: {e}")
