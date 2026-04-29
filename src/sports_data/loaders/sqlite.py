import logging
import hashlib
from typing import Any, List, Dict
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Float, Date, DateTime, PrimaryKeyConstraint, Index
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.dialects.sqlite import insert
from sports_data.core.interfaces import BaseLoader

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

class FactMatchLog(Base):
    __tablename__ = 'fact_match_logs'

    match_id = Column(String, primary_key=True)
    fbref_team_id = Column(String, index=True)
    season = Column(String)
    match_date = Column(Date, index=True)
    competition = Column(String)
    venue = Column(String)
    opponent_name = Column(String)
    result = Column(String, nullable=True)
    goals_for = Column(Integer, nullable=True)
    goals_against = Column(Integer, nullable=True)
    xg_for = Column(Float, nullable=True)
    xg_against = Column(Float, nullable=True)
    possession_pct = Column(Integer, nullable=True)
    updated_at = Column(DateTime)

class SQLiteMatchLoader(BaseLoader):
    def __init__(self, db_path: str = "sqlite:///sports_data.db"):
        self.engine = create_engine(db_path)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def load(self, data: List[Dict[str, Any]]) -> None:
        if not data:
            logger.info("No data to load.")
            return

        session = self.Session()
        try:
            records = []
            for row in data:
                # MD5 hash for match_id: fbref_team_id + match_date
                match_id_raw = f"{row['fbref_team_id']}_{row['match_date'].isoformat()}"
                match_id = hashlib.md5(match_id_raw.encode('utf-8')).hexdigest()

                row_dict = {
                    "match_id": match_id,
                    "fbref_team_id": row["fbref_team_id"],
                    "season": row["season"],
                    "match_date": row["match_date"],
                    "competition": row["competition"],
                    "venue": row["venue"],
                    "opponent_name": row["opponent_name"],
                    "result": row["result"],
                    "goals_for": row["goals_for"],
                    "goals_against": row["goals_against"],
                    "xg_for": row["xg_for"],
                    "xg_against": row["xg_against"],
                    "possession_pct": row["possession_pct"],
                    "updated_at": datetime.now()
                }
                records.append(row_dict)

            # SQLite UPSERT
            stmt = insert(FactMatchLog).values(records)

            # On conflict on match_id, update all columns except match_id
            update_dict = {c.name: c for c in stmt.excluded if c.name != 'match_id'}

            do_update_stmt = stmt.on_conflict_do_update(
                index_elements=['match_id'],
                set_=update_dict
            )

            session.execute(do_update_stmt)
            session.commit()
            logger.info(f"Loaded {len(records)} records into fact_match_logs.")

        except Exception as e:
            session.rollback()
            logger.error(f"Error loading data: {e}")
            raise
        finally:
            session.close()
