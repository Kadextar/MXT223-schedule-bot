from fastapi import FastAPI
from fastapi.responses import FileResponse
from core.analytics import analyze_week_load
from core.schedule_service import format_today_schedule

app = FastAPI(title="MXT-223 Web API")


@app.get("/")
def index():
    return FileResponse("web/index.html")


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
