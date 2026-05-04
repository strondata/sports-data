import pytest
from sports_data.extractors.local import LocalFBRefExtractor
from sports_data.core.exceptions import ExtractionError

def test_local_extractor_success():
    extractor = LocalFBRefExtractor(file_path="data/raw_samples/bayern_mock.html")
    result = extractor.extract()

    assert "url" in result
    assert len(result["data"]) == 6
    assert result["data"][0]["Date"] == "2025-08-20"
    assert result["data"][0]["Opponent"] == "Dortmund"

def test_local_extractor_missing_file():
    extractor = LocalFBRefExtractor(file_path="missing_file.html")
    with pytest.raises(ExtractionError, match="Local file not found"):
        extractor.extract()
