# chronos_gemini_google_search.py
import os, json, requests, time, re
import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
from google import genai  # from 'google-genai' SDK
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# --- Config ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
GEMINI_MODEL = "models/gemini-2.5-flash-lite"
SEARCH_BACKEND = "duckduckgo"  # switch to "google" later, no other changes needed
# ---------------

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


def call_gemini(fragment):
    """Send the fragment to Gemini and return parsed JSON."""
    prompt = f"""
    You are Chronos, an AI Archeologist. Your mission is to reconstruct incomplete or obscure digital text.

    Input Fragment:
    "{fragment}"

    Produce JSON only with the following fields:
    - reconstructed_text: plausible completion of the fragment.
    - rationale: short reasoning.
    - confidence: float between 0 and 1.
    - keywords: list of 3-5 important search keywords.

    If uncertain, mention that in rationale.
    """

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    raw_text = getattr(response, "text", None) or str(response)
    cleaned = re.sub(r"```json\s*|\s*```", "", raw_text, flags=re.MULTILINE).strip()
    try:
        jstart = cleaned.index("{")
        json_text = cleaned[jstart:]
        result = json.loads(json_text)
    except Exception:
        result = {"reconstructed_text": raw_text.strip(), "rationale": "", "confidence": 0.0, "keywords": []}
    return result


def generate_queries(gemini_output):
    """Convert Gemini output into plain text queries suitable for search"""
    queries = {}
    reconstructed_text = gemini_output.get("reconstructed_text", "").strip()
    keywords_text = " ".join(gemini_output.get("keywords", [])).strip()

    if reconstructed_text:
        queries['reconstructed_text'] = reconstructed_text
    if keywords_text:
        queries['keywords_text'] = keywords_text

    return queries


def google_custom_search(query, num=5):
    """Query Google Custom Search JSON API."""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_SEARCH_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": num
    }
    r = requests.get(url, params=params, timeout=15)
    if r.status_code != 200:
        print(f"   [DEBUG] Status {r.status_code}: {r.text}")
    r.raise_for_status()
    data = r.json()
    results = []
    for item in data.get("items", [])[:num]:
        results.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet")
        })
    return results


def web_search(query, num=3):
    """Query DuckDuckGo's HTML search results (no API key required)."""
    url = "https://html.duckduckgo.com/html/"
    params = {"q": query}
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, params=params, headers=headers, timeout=15)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    results = []
    for result in soup.select(".result__title a")[:num]:
        title = result.get_text(strip=True)
        link = result.get("href")
        results.append({"title": title, "link": link, "snippet": ""})
    return results


def print_report(original_fragment, reconstruction, sources, confidence=1.0, rationale=""):
    print("\n" + "=" * 60)
    print("           CHRONOS RECONSTRUCTION REPORT")
    print("=" * 60)
    print("\nORIGINAL FRAGMENT")
    print(f'   "{original_fragment}"')
    print("\nRECONSTRUCTED TEXT")
    if confidence < 0.4:
        print(f'   No confident reconstruction found for this fragment.')
        if rationale:
            print(f'   ({rationale})')
    else:
        print(f'   "{reconstruction}"')
    print("\nCONTEXTUAL SOURCES")
    found_any = False
    for item in sources.get('reconstructed_text', []):
        if isinstance(item, dict) and 'link' in item:
            print(f"   - {item['link']}")
            found_any = True
    if not found_any:
        print("   (no sources found)")
    print("\n" + "=" * 60 + "\n")

def main():
    print("\n" + "=" * 60)
    print("     PROJECT CHRONOS — THE AI ARCHEOLOGIST")
    print("=" * 60)
    fragment = input("\nEnter fragmented or old internet text:\n> ")

    print("\n[1/2] Reconstructing with Gemini...")
    reconstruction = call_gemini(fragment)

    queries = generate_queries(reconstruction)

    print("[2/2] Searching for cultural context...")
    all_results = {}
    for q in queries:
        try:
            if SEARCH_BACKEND == "google":
                results = google_custom_search(queries[q], num=3)
            else:
                results = web_search(queries[q], num=3)
            all_results[q] = results if results else []
        except Exception as e:
            print(f"   [DEBUG] Search failed for '{q}': {e}")
            all_results[q] = {"error": str(e)}

    reconstruction_text = queries.get('reconstructed_text', '(no reconstruction available)')
    confidence = reconstruction.get('confidence', 1.0)
    rationale = reconstruction.get('rationale', '')
    print_report(fragment, reconstruction_text, all_results, confidence, rationale)

if __name__ == "__main__":
    main()