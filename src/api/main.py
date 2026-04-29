from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from typing import List, Dict, Any
import logging
from sports_data.loaders.sqlite import FactMatchLog

# Structured Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sports Data API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup DB Connection
DATABASE_URL = "sqlite:///sports_data.db"
engine = create_engine(DATABASE_URL)

def get_db():
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/v1/teams/{fbref_team_id}/matches")
def get_matches(fbref_team_id: str, db: Session = Depends(get_db)):
    """Returns all matches for a specific team."""
    matches = db.query(FactMatchLog).filter(FactMatchLog.fbref_team_id == fbref_team_id).order_by(FactMatchLog.match_date.desc()).all()

    if not matches:
        raise HTTPException(status_code=404, detail="Team or matches not found")

    return matches

@app.get("/api/v1/teams/{fbref_team_id}/insights")
def get_insights(fbref_team_id: str, db: Session = Depends(get_db)):
    """Returns pre-calculated metrics for a specific team."""

    # Get last 5 matches to calculate avg xG
    last_5_matches = db.query(FactMatchLog).filter(
        FactMatchLog.fbref_team_id == fbref_team_id,
        FactMatchLog.xg_for.isnot(None)
    ).order_by(FactMatchLog.match_date.desc()).limit(5).all()

    avg_xg_last_5 = None
    if last_5_matches:
        total_xg = sum(m.xg_for for m in last_5_matches if m.xg_for is not None)
        avg_xg_last_5 = round(total_xg / len(last_5_matches), 2)

    # Home vs Away Performance
    home_matches = db.query(FactMatchLog).filter(
        FactMatchLog.fbref_team_id == fbref_team_id,
        FactMatchLog.venue == 'Home',
        FactMatchLog.result.isnot(None)
    ).all()

    away_matches = db.query(FactMatchLog).filter(
        FactMatchLog.fbref_team_id == fbref_team_id,
        FactMatchLog.venue == 'Away',
        FactMatchLog.result.isnot(None)
    ).all()

    def calc_win_rate(matches_list):
        if not matches_list:
            return 0.0
        wins = sum(1 for m in matches_list if m.result == 'W')
        return round((wins / len(matches_list)) * 100, 2)

    home_win_rate = calc_win_rate(home_matches)
    away_win_rate = calc_win_rate(away_matches)

    return {
        "fbref_team_id": fbref_team_id,
        "avg_xg_last_5_matches": avg_xg_last_5,
        "home_win_rate_pct": home_win_rate,
        "away_win_rate_pct": away_win_rate
    }
