import typer
import logging
from sports_data.core.pipeline import ETLPipeline
from sports_data.extractors.local import LocalFBRefExtractor
from sports_data.transformers.fbref import MatchLogTransformer
from sports_data.loaders.sqlite import SQLiteMatchLoader

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)

logger = logging.getLogger(__name__)

app = typer.Typer(help="Sports Data ETL CLI")

@app.command()
def run(url: str = typer.Argument(..., help="The FBref URL to scrape")):
    """
    Runs the ETL pipeline for a given FBref match logs URL.
    """
    logger.info(f"Starting CLI run for URL: {url}")

    extractor = LocalFBRefExtractor()
    transformer = MatchLogTransformer()
    loader = SQLiteMatchLoader()

    pipeline = ETLPipeline(
        extractor=extractor,
        transformer=transformer,
        loader=loader
    )

    try:
        pipeline.run(url=url)
        logger.info("CLI run completed successfully.")
    except Exception as e:
        logger.error(f"CLI run failed: {e}")
        raise typer.Exit(code=1)

def cli():
    app()

if __name__ == "__main__":
    cli()
