import csv, os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_core.tools import tool

load_dotenv()

SHEET_PATH = "stock_research.csv"
FIELDS = ["ticker", "price", "pe_ratio", "revenue_m", "analyst_view"]

class StockRow(BaseModel):
    ticker: str
    price: float
    pe_ratio: float
    revenue_m: float
    analyst_view: str

SERPER_KEY = os.environ["SERPER_API_KEY"]

@tool
def search_web(query: str) -> str:
    """Search the web for stock data, news, or analyst views."""
    try:
        r = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_KEY},
            json={"q": query},
            timeout=10,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        return f"Error searching web: {e}"
    results = r.json().get("organic", [])
    return "\n\n".join([f"{r['title']}\n{r['link']}\n{r['snippet']}"
                        for r in results[:5]])

@tool
def read_url(url: str) -> str:
    """Fetch and read the content of a URL."""
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
    except requests.RequestException as e:
        return f"Error reading {url}: {e}"
    return r.text[:3000]

@tool
def write_to_sheet(rows: list[StockRow]) -> str:
    """Write all research rows to the tracker sheet in one call."""
    exists = os.path.exists(SHEET_PATH)
    with open(SHEET_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerows([row.model_dump() for row in rows])
    return f"Wrote {len(rows)} rows to {SHEET_PATH}"
