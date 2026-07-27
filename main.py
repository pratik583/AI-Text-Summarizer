import os

from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import clear_history, get_recent, init_db, save_summary
from summarizer import summarize

app = FastAPI(title="AI Text Summarizer (local, free)")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def home(request: Request):
    history = get_recent(limit=5)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "result": None, "history": history, "text": ""},
    )


@app.post("/summarize")
def do_summarize(
    request: Request,
    text: str = Form(...),
    num_sentences: int = Form(3),
):
    num_sentences = max(1, min(num_sentences, 20))
    result = summarize(text, num_sentences=num_sentences)

    if result["summary"]:
        save_summary(text, result["summary"])

    history = get_recent(limit=5)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result,
            "history": history,
            "text": text,
            "num_sentences": num_sentences,
        },
    )


@app.post("/clear-history")
def clear():
    clear_history()
    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    # Lets `python main.py` work too, and respects the $PORT env var that
    # most free hosting platforms (Render, Railway, etc.) inject automatically.
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
