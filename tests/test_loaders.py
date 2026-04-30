import pytest
from datetime import date
from sports_data.loaders.sqlite import SQLiteMatchLoader, FactMatchLog

@pytest.fixture
def loader():
    # Use in-memory SQLite for testing
    loader = SQLiteMatchLoader(db_path="sqlite:///:memory:")
    return loader

def test_sqlite_loader(loader):
    data = [
        {
            "fbref_team_id": "054efa67",
            "season": "2025-2026",
            "match_date": date(2025, 8, 20),
            "competition": "Bundesliga",
            "venue": "Home",
            "opponent_name": "Dortmund",
            "result": "W",
            "goals_for": 2,
            "goals_against": 1,
            "xg_for": 1.5,
            "xg_against": 0.8,
            "possession_pct": 60
        }
    ]

    loader.load(data)

    session = loader.Session()
    results = session.query(FactMatchLog).all()
    session.close()

    assert len(results) == 1
    assert results[0].fbref_team_id == "054efa67"
    assert results[0].goals_for == 2

def test_sqlite_loader_upsert(loader):
    data = [
        {
            "fbref_team_id": "054efa67",
            "season": "2025-2026",
            "match_date": date(2025, 8, 20),
            "competition": "Bundesliga",
            "venue": "Home",
            "opponent_name": "Dortmund",
            "result": None,
            "goals_for": None,
            "goals_against": None,
            "xg_for": None,
            "xg_against": None,
            "possession_pct": None
        }
    ]

    # First load (unplayed match)
    loader.load(data)

    # Update data (match played)
    data[0]["result"] = "W"
    data[0]["goals_for"] = 2
    data[0]["goals_against"] = 1

    # Second load (should UPSERT)
    loader.load(data)

    session = loader.Session()
    results = session.query(FactMatchLog).all()
    session.close()

    assert len(results) == 1
    assert results[0].result == "W"
    assert results[0].goals_for == 2
