class RateLimitError(Exception):
    """Raised when rate limit is exceeded."""
    pass

class ExtractionError(Exception):
    """Raised when data extraction fails."""
    pass

class TransformationError(Exception):
    """Raised when data transformation fails."""
    pass

class LoadingError(Exception):
    """Raised when data loading fails."""
    pass
