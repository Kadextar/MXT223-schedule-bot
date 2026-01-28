import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from core.analytics import analyze_week_load
from core.schedule_service import format_today_schedule

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="MXT-223 Web API")

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "web", "static")),
    name="static"
)

@app.get("/")
def index():
    return FileResponse(os.path.join(BASE_DIR, "web", "index.html"))


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "MXT-223 schedule web",
    }


@app.get("/api/week-load")
def week_load():
    return analyze_week_load()


@app.get("/api/today")
def today():
    return {
        "text": format_today_schedule()
    }
