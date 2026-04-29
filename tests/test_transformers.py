import pytest
from datetime import date
from sports_data.transformers.fbref import MatchLogTransformer
from sports_data.core.exceptions import TransformationError

def test_matchlog_transformer():
    url = "https://fbref.com/en/squads/054efa67/2025-2026/matchlogs/all_comps/schedule/test"
    raw_data = {
        "url": url,
        "data": [
            {
                "Date": "2025-08-20",
                "Comp": "Bundesliga",
                "Venue": "Home",
                "Opponent": "Dortmund",
                "Result": "W",
                "GF": "2",
                "GA": "1",
                "xG": "1.5",
                "xGA": "0.8",
                "Poss": "60"
            },
            {
                "Date": "2025-08-27",
                "Comp": "Bundesliga",
                "Venue": "Away",
                "Opponent": "Leipzig",
                "Result": "",  # Unplayed
                "GF": "",
                "GA": "",
                "xG": "",
                "xGA": "",
                "Poss": ""
            }
        ]
    }

    transformer = MatchLogTransformer()
    transformed = transformer.transform(raw_data)

    assert len(transformed) == 2

    # Check first match (played)
    match1 = transformed[0]
    assert match1["fbref_team_id"] == "054efa67"
    assert match1["season"] == "2025-2026"
    assert match1["match_date"] == date(2025, 8, 20)
    assert match1["goals_for"] == 2
    assert match1["xg_for"] == 1.5
    assert match1["result"] == "W"

    # Check second match (unplayed)
    match2 = transformed[1]
    assert match2["result"] is None
    assert match2["goals_for"] is None
    assert match2["xg_for"] is None

def test_matchlog_transformer_invalid_url():
    raw_data = {
        "url": "https://fbref.com/invalid_url",
        "data": [{"Date": "2025-08-20"}]
    }

    transformer = MatchLogTransformer()
    with pytest.raises(TransformationError):
        transformer.transform(raw_data)
