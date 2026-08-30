import requests, os
from dotenv import load_dotenv

load_dotenv()

SERPER_KEY = os.environ["SERPER_API_KEY"]

def search_web(query: str) -> str:
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

def read_url(url: str) -> str:
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
    except requests.RequestException as e:
        return f"Error reading {url}: {e}"
    return r.text[:3000]

def write_file(filename: str, content: str) -> str:
    with open(filename, "w") as f:
        f.write(content)
    return f"Saved to {filename}"