# Agents

This repository uses a structured ETL framework. Please follow these principles:
- **Open/Closed Principle (SOLID):** The core classes (`BaseExtractor`, `BaseTransformer`, `BaseLoader`) must be open to extension but closed to modification.
- **Dependency Injection (DI):** ETL flow orchestration must happen in the `ETLPipeline` class that receives instances of extraction, transformation and loading.
- **Idempotency:** Loading layer must ensure no duplicates exist using specific primary keys.
- **Structured Logging:** `print()` is forbidden. Use Python's `logging` module.

## Database (Gold Layer)
**Table: `fact_match_logs`**
- `match_id` (PK, String): MD5 hash of `fbref_team_id` + `match_date`.
- `fbref_team_id` (String, Indexed)
- `season` (String)
- `match_date` (Date, Indexed)
- `competition` (String)
- `venue` (String)
- `opponent_name` (String)
- `result` (String)
- `goals_for` (Integer)
- `goals_against` (Integer)
- `xg_for` (Float)
- `xg_against` (Float)
- `possession_pct` (Integer)
- `updated_at` (Timestamp)
