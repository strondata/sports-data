import pytest
import responses
from sports_data.extractors.fbref import FBRefMatchLogExtractor
from sports_data.core.exceptions import RateLimitError, ExtractionError

MOCK_HTML = """
<html>
  <body>
    <table id="matchlogs_for">
      <thead>
        <tr>
          <th>Date</th><th>Comp</th><th>Venue</th><th>Opponent</th><th>Result</th><th>GF</th><th>GA</th><th>xG</th><th>xGA</th><th>Poss</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>2025-08-20</td><td>Bundesliga</td><td>Home</td><td>Dortmund</td><td>W</td><td>2</td><td>1</td><td>1.5</td><td>0.8</td><td>60</td>
        </tr>
      </tbody>
    </table>
  </body>
</html>
"""

@responses.activate
def test_fbref_extractor_success():
    url = "https://fbref.com/en/squads/054efa67/2025-2026/matchlogs/all_comps/schedule/Bayern-Munich-Scores-and-Fixtures-All-Competitions"
    responses.add(responses.GET, url, body=MOCK_HTML, status=200)

    # Set delay to 0 for tests
    extractor = FBRefMatchLogExtractor(delay=0)
    result = extractor.extract(url=url)

    assert result["url"] == url
    assert len(result["data"]) == 1
    assert result["data"][0]["Date"] == "2025-08-20"
    assert result["data"][0]["Opponent"] == "Dortmund"

@responses.activate
def test_fbref_extractor_rate_limit():
    url = "https://fbref.com/rate_limit_url"
    responses.add(responses.GET, url, status=429)

    extractor = FBRefMatchLogExtractor(delay=0)
    with pytest.raises(RateLimitError):
        extractor.extract(url=url)

@responses.activate
def test_fbref_extractor_missing_table():
    url = "https://fbref.com/missing_table"
    responses.add(responses.GET, url, body="<html><body>No table here</body></html>", status=200)

    extractor = FBRefMatchLogExtractor(delay=0)
    with pytest.raises(ExtractionError, match="Table 'matchlogs_for' not found"):
        extractor.extract(url=url)
