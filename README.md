# Project Chronos: The AI Archeologist

**Student:** Naga Sai Karthikeya M
**Roll No.:** SE25UCSE084

## Project Description

Project Chronos is an AI-powered tool that reconstructs fragmented, obscure, or slang-filled text from old internet sources — forum posts, old chat logs, early social media — and provides cultural context for the reconstruction. It uses Google's Gemini API to intelligently fill in missing meaning based on linguistic style and subject matter, then automatically searches the web to surface relevant sources that support the reconstruction. The final output is a clean, structured "Reconstruction Report" showing the original fragment, the AI's interpretation, and supporting context links.

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd Project_chronos
```

### 2. Install dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Set up API keys
Create a `.env` file in the project root with the following: 
GEMINI_API_KEY=your_gemini_api_key_here

Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

> **Note:** By default, this project uses DuckDuckGo's free search endpoint for contextual sources, which requires no API key. To use Google Custom Search API instead, add `GOOGLE_SEARCH_API_KEY` and `GOOGLE_CSE_ID` to `.env`, and change `SEARCH_BACKEND = "duckduckgo"` to `SEARCH_BACKEND = "google"` at the top of `chronos.py`.

## Usage

Run the program from the terminal:
```bash
python3 chronos.py
```

You'll be prompted to enter a fragment of old or obscure internet text: