from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from core.analytics import analyze_week_load
from core.schedule_service import format_today_schedule

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="MXT-223 Web API")

# ✅ ПРАВИЛЬНЫЙ STATIC
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "web" / "static"),
    name="static"
)

@app.get("/")
def index():
    return FileResponse(BASE_DIR / "web" / "index.html")

@app.get("/api/week-load")
def week_load():
    return analyze_week_load()

@app.get("/api/today")
def today():
    return {"text": format_today_schedule()}