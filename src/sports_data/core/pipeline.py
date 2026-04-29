import logging
from typing import Any
from .interfaces import BaseExtractor, BaseTransformer, BaseLoader

logger = logging.getLogger(__name__)

class ETLPipeline:
    def __init__(self, extractor: BaseExtractor, transformer: BaseTransformer, loader: BaseLoader):
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader

    def run(self, **kwargs: Any) -> None:
        logger.info("Starting ETL pipeline")
        try:
            logger.info("Extracting data...")
            raw_data = self.extractor.extract(**kwargs)
            logger.info("Transforming data...")
            clean_data = self.transformer.transform(raw_data)
            logger.info("Loading data...")
            self.loader.load(clean_data)
            logger.info("ETL pipeline completed successfully")
        except Exception as e:
            logger.error(f"ETL pipeline failed: {e}", exc_info=True)
            raise
