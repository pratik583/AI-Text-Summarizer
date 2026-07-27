# AI Text Summarizer (local AI, 100% free, deployable)

A small full-stack app that summarizes long text using a **local, offline AI
technique** — no API key, no cloud LLM calls, no per-request cost, and light
enough to deploy on free hosting tiers.

## How the "AI" works

This uses **extractive summarization** with the classic **TextRank** algorithm:

1. Split the input into sentences.
2. Turn each sentence into a TF-IDF vector (how important each word is).
3. Build a similarity graph between all sentences (cosine similarity).
4. Run PageRank over that graph to rank sentences by importance —
   the same idea Google used to rank web pages, applied to sentences.
5. Return the top N highest-ranked sentences, in their original order.

No neural network weights to download, no GPU needed, and it runs in
milliseconds on a free-tier server. This is a legitimate, well-established
summarization technique (it's what libraries like `sumy` and many older
production summarizers use) — the tradeoff vs. a large language model is
that it selects existing sentences rather than generating new phrasing.

## Project structure

```
ai-summarizer-app/
├── main.py             # FastAPI app & routes
├── summarizer.py        # TextRank summarization logic
├── database.py          # SQLite storage for recent summaries
├── requirements.txt     # Python dependencies (all free/open-source)
├── Procfile             # For Render/Railway/Heroku-style deployment
├── templates/
│   └── index.html        # Jinja2 template (the whole UI)
└── static/
    └── style.css          # Styling
```

## Run it locally

1. Python 3.9+ required. Create and activate a virtual environment:

   **macOS/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   **Windows (PowerShell):**
   ```powershell
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:

   ```bash
   uvicorn main:app --reload
   ```

4. Open **http://127.0.0.1:8000**, paste in some text, pick a summary
   length, and hit Summarize.

Recent summaries are saved to a local `history.db` SQLite file (delete it
any time to reset).

## Deploying it for free

The app reads the `$PORT` environment variable, so it's ready to deploy on
any platform with a free tier for small Python web services, for example:

### Render (free web service)
1. Push this project to a GitHub repo.
2. On Render, choose **New Web Service**, connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   (or Render will auto-detect the `Procfile`)
5. Deploy — Render's free tier will spin the service up (it may sleep after
   inactivity and take a few seconds to wake back up).

### Railway / Fly.io
Similar flow — connect the repo, they detect the `Procfile` automatically,
and deploy on their free/trial allowance.

**Note:** free tiers and their limits change over time and vary by
provider, so check current terms before relying on one long-term. Because
this app has no heavy ML dependencies (no PyTorch, no downloaded model
weights), it stays well within typical free-tier memory limits (usually
256–512MB), unlike apps built on large transformer models.

## Extending it

- Swap in a real transformer-based summarizer (e.g. via Hugging Face
  `transformers`) if you want abstractive (rewritten) summaries — this
  needs more memory/CPU and may not fit comfortably on the smallest free
  tiers.
- Add a "summarize from URL" feature that fetches and cleans article text.
- Add user accounts so each person has their own history.
