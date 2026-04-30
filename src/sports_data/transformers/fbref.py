import logging
import re
from typing import Any
import pandas as pd
from datetime import datetime
from sports_data.core.interfaces import BaseTransformer
from sports_data.core.exceptions import TransformationError

logger = logging.getLogger(__name__)

class MatchLogTransformer(BaseTransformer):
    def transform(self, raw_data: Any) -> Any:
        url = raw_data.get("url", "")
        data_records = raw_data.get("data", [])

        if not data_records:
            return []

        # Extract fbref_team_id and season from URL
        # Example URL: https://fbref.com/en/squads/054efa67/2025-2026/matchlogs/all_comps/schedule/Bayern-Munich-Scores-and-Fixtures-All-Competitions

        match = re.search(r'/squads/([^/]+)/([^/]+)/', url)
        if not match:
            logger.error("Could not extract team ID and season from URL")
            raise TransformationError("Invalid URL format for team ID and season extraction")

        fbref_team_id = match.group(1)
        season = match.group(2)

        df = pd.DataFrame(data_records)

        transformed_data = []

        for _, row in df.iterrows():
            # Skip empty or summary rows
            if pd.isna(row.get('Date')) or not isinstance(row.get('Date'), str):
                continue

            try:
                date_str = str(row.get('Date')).strip()
                # ISO 8601 conversion (YYYY-MM-DD)
                match_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                continue

            comp = str(row.get('Comp', ''))
            venue = str(row.get('Venue', ''))
            opponent = str(row.get('Opponent', ''))

            result_raw = row.get('Result', '')
            result = str(result_raw) if pd.notna(result_raw) and result_raw != '' else None
            if result not in ['W', 'D', 'L']:
                result = None

            # Handle numeric columns safely
            def to_int(val):
                if pd.isna(val) or val == '':
                    return None
                try:
                    return int(float(val))
                except ValueError:
                    return None

            def to_float(val):
                if pd.isna(val) or val == '':
                    return None
                try:
                    return float(val)
                except ValueError:
                    return None

            goals_for = to_int(row.get('GF'))
            goals_against = to_int(row.get('GA'))
            xg_for = to_float(row.get('xG'))
            xg_against = to_float(row.get('xGA'))
            possession = to_int(row.get('Poss'))

            transformed_data.append({
                "fbref_team_id": fbref_team_id,
                "season": season,
                "match_date": match_date,
                "competition": comp,
                "venue": venue,
                "opponent_name": opponent,
                "result": result,
                "goals_for": goals_for,
                "goals_against": goals_against,
                "xg_for": xg_for,
                "xg_against": xg_against,
                "possession_pct": possession
            })

        return transformed_data
