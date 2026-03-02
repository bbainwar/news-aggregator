# Project Specification: Automated Daily News Aggregator

## Objective
Build a lightweight FastAPI backend that uses the Gemini API (with Google Search Grounding) to fetch real-time news, format it as an HTML email, and send it daily at a scheduled time. 

## Tech Stack
* **Framework:** FastAPI (Python 3.11+)
* **AI/Search:** `google-genai` (The latest official Google GenAI SDK, NOT the legacy `google-generativeai` package)
* **Scheduling:** `apscheduler` (`AsyncIOScheduler`)
* **Email:** Standard Python `smtplib` and `email` modules
* **Environment Management:** `python-dotenv`
* **Logging:** Standard Python `logging` module

## Architecture & Core Flows
The application should be modular and avoid unnecessary complexity (no databases, no message queues). All modules must include proper logging and error handling.

### 1. `main.py` (Entrypoint & Orchestration)
* Initialize the FastAPI app using the modern `@asynccontextmanager` lifespan approach to handle the scheduler startup and shutdown.
* Configure logging at startup (INFO level, with timestamps and module names).
* Configure `AsyncIOScheduler` to run the email generation and sending job daily. The schedule should be configurable via environment variables (`SCHEDULE_HOUR`, `SCHEDULE_MINUTE`, `SCHEDULE_TZ`), defaulting to 8:00 AM IST (`Asia/Kolkata`).
* Create a `POST /trigger-email` endpoint that uses FastAPI's `BackgroundTasks` to manually trigger the pipeline for testing purposes without blocking the HTTP response.

### 2. `services/news_service.py` (Data & AI Layer)
* Initialize the Gemini client with the API key from the environment: `client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))`.
* The model name should be read from the `GEMINI_MODEL` environment variable, defaulting to `gemini-2.5-flash`.
* Create a function `fetch_and_format_news() -> str` that prompts the configured model.
* **Prompt Instructions:** "You are an expert news editor. Search the web for the top 3 most important news stories today in: 1. World News, 2. Global Tech News, 3. India News, 4. Nepal News. Format strictly as a clean, minimalist HTML email using `<h2>` for categories and `<ul>`/`<li>` for items. Include headlines, a 1-sentence summary, and a hyperlink to the source. Do NOT wrap the output in markdown code blocks."
* **CRITICAL - Google Search Grounding:** You must explicitly enable the search tool in the API call using the new SDK syntax:
    ```python
    from google import genai
    from google.genai import types
    
    config = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.2,
    )
    # Pass this config to client.models.generate_content
    ```
* **Error Handling:** Wrap the API call in a `try/except` block. Log any exceptions (rate limits, timeouts, malformed responses) and re-raise so the caller can handle them. If the response contains markdown code fences (e.g., ` ```html `), strip them before returning.

### 3. `services/email_service.py` (Delivery Layer)
* Create a function `send_news_email(html_content: str)` that takes the raw HTML string from the Gemini response.
* Use `MIMEMultipart("alternative")` to construct the email.
* Connect to `smtp.gmail.com` on port 465 using `smtplib.SMTP_SSL`.
* Authenticate and send using credentials loaded from environment variables.
* **Error Handling:** Wrap SMTP operations in a `try/except` block. Log connection failures, authentication errors, and send failures with descriptive messages.

### 4. `services/pipeline.py` (Orchestration)
* Create a `run_pipeline()` function that calls `fetch_and_format_news()` and then `send_news_email()`.
* Wrap the full pipeline in a `try/except` so that a failure in one step is logged but does not crash the scheduler or the server.

## Environment Variables Needed (`.env`)
* `GOOGLE_API_KEY` (Gemini API key — this is the env var the `google-genai` SDK expects)
* `GEMINI_MODEL` (optional, defaults to `gemini-2.5-flash`)
* `SENDER_EMAIL`
* `SENDER_PASSWORD` (Gmail App Password)
* `RECEIVER_EMAIL`
* `SCHEDULE_HOUR` (optional, defaults to `8`)
* `SCHEDULE_MINUTE` (optional, defaults to `0`)
* `SCHEDULE_TZ` (optional, defaults to `Asia/Kolkata`)

## Expected Output from Agent
* Complete project structure with all necessary Python files.
* `requirements.txt` with pinned major versions for reproducibility.
* A `.env.example` file listing all required and optional variables with placeholder values.
* The application must be runnable immediately via `uvicorn main:app --reload`.