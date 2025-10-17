# chronos_gemini_google_search.py
import os, json, requests, time
from dotenv import load_dotenv
from google import genai  # from 'google-genai' SDK
import re

# Load environment variables
load_dotenv()

# --- Config ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
GEMINI_MODEL = "models/gemini-2.5-flash-lite"  # or "gemini-1.5-flash"
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
    try:
        jstart = raw_text.index("{")
        json_text = raw_text[jstart:]
        result = json.loads(json_text)
    except Exception:
        result = {"reconstructed_text": raw_text.strip(), "rationale": "", "confidence": 0.0, "keywords": []}
    return result

import json
import re

def generate_queries(gemini_output):
    """Convert Gemini output into plain text queries suitable for Google search"""
    queries = {}

    # Step 1: Get the raw reconstructed_text
    raw_text = gemini_output.get("reconstructed_text", "")

    # Step 2: Remove ```json and ``` markers if present
    cleaned_text = re.sub(r"```json\s*|\s*```", "", str(raw_text), flags=re.MULTILINE).strip()

    # Step 3: Try parsing JSON inside cleaned_text
    try:
        inner = json.loads(cleaned_text)
        reconstructed_text = inner.get("reconstructed_text", "").strip()
        keywords_text = " ".join(inner.get("keywords", [])).strip()
    except json.JSONDecodeError:
        # If parsing fails, fallback: use cleaned_text as is
        reconstructed_text = cleaned_text
        keywords_text = " ".join(gemini_output.get("keywords", [])).strip()

    # Step 4: Add to queries list
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


def print_report(original_fragment, reconstruction, sources):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    # report = {
    #     "project": "Project Chronos",
    #     "timestamp": timestamp,
    #     "original_fragment": original_fragment,
    #     "reconstruction": reconstruction,
    #     "sources": sources
    # }
    print("--- RECONSTRUCTION REPORT ---\n")
    print("[Original Fragment]\n")
    print("> "+"\""+original_fragment+"\"\n")
    print("[AI-Reconstructed Text]\n")
    print("> "+"\""+reconstruction+"\"\n")
    print("[Contextual Sources]")
    for item in sources['reconstructed_text']:
        print('* '+item['link']+'\n')


    #return report


# def save_report(report):
#     fname = "chronos_report.json"
#     with open(fname, "w", encoding="utf-8") as f:
#         json.dump(report, f, indent=2, ensure_ascii=False)
#     print(f"\n Reconstruction Report saved as {fname}")


def main():
    print("Project Chronos — The AI Archeologist\n")
    fragment = input("Enter fragmented or old internet text: ")

    print("\n[*] Sending to Gemini for reconstruction...")
    reconstruction = call_gemini(fragment)
    #print(f"Reconstructed Text:\n{reconstruction['reconstructed_text']}")
    #print("\n[*] Searching for cultural context via Google Custom Search...")

    queries = generate_queries(reconstruction)
    all_results = {}
    for q in queries:
        try:
            results = google_custom_search(q, num=3)
            all_results[q] = results if results else []
            print(f"Query: {q} — {len(results)} results")
        except Exception as e:
            all_results[q] = {"error": str(e)}

    #report = build_report(fragment, queries['reconstructed_text'], all_results)
    report = print_report(fragment, queries['reconstructed_text'], all_results)
    #save_report(report)


if __name__ == "__main__":
    main()
