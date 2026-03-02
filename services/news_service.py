import os
import re
import logging

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

NEWS_PROMPT = (
    """You are an expert, objective news editor curating a daily news briefing. 

Execute a web search to find the top 5 most important, breaking news stories from the LAST 24 HOURS for each of the following categories. Prioritize high-quality, trusted journalistic sources:
1. World News (e.g., Reuters, AP, BBC)
2. Global Tech News (e.g., TechCrunch, The Verge, Bloomberg Technology, Ars Technica)
3. India News (e.g., The Hindu, Indian Express, Mint, NDTV)
4. Nepal News (e.g., Kathmandu Post, Nepali Times, OnlineKhabar)

Curation Rules:
- No Repetition: Strictly ensure diversity of topics. Do not include multiple articles about the exact same event.
- Find minimum 5 stories for each category and all of it should be high quality news.

Formatting Rules:
- Output STRICTLY as a clean, minimalist HTML email. Do NOT wrap the output in markdown code blocks (no ```html).
- Add basic inline CSS to the <body> tag for readability: font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 800px; margin: auto;
- Include a main header: <h1>Daily News Briefing - [Insert Today's Date]</h1>
- Use <h2> for category headers.
- Use <ul> and <li> for news items.
- Structure each item exactly like this: <strong>Headline</strong> - <em>1-sentence objective summary.</em> <a href="URL">[Read Source]</a>"""
)


def _strip_markdown_fences(text: str) -> str:
    """Remove markdown code fences (```html ... ```) if present."""
    return re.sub(r"^```(?:html)?\s*\n?|```\s*$", "", text, flags=re.MULTILINE).strip()


def fetch_and_format_news() -> str:
    """Fetch today's top news using Gemini with Google Search grounding and
    return the result as an HTML string."""
    logger.info("Fetching news using model: %s", GEMINI_MODEL)

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    config = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.2,
    )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=NEWS_PROMPT,
            config=config,
        )
    except Exception:
        logger.exception("Gemini API call failed")
        raise

    html = response.text
    html = _strip_markdown_fences(html)

    logger.info("Successfully fetched and formatted news (%d chars)", len(html))
    return html
