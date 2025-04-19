from fastapi import FastAPI, Request
from pydantic import BaseModel
from modelAIFin import get_event_summary
from fastapi.responses import HTMLResponse

app = FastAPI()

# For GET requests (HTML-style browser rendering)
@app.get("/summary", response_class=HTMLResponse)
async def get_summary(event_name: str = ""):
    summary = get_event_summary(event_name)
    return f"<pre>{summary}</pre>"

# For POST requests (API-style usage)
class EventRequest(BaseModel):
    event_name: str

@app.post("/api/summary")
async def post_summary(request_data: EventRequest):
    summary = get_event_summary(request_data.event_name)
    return {
        "event_name": request_data.event_name,
        "summary": summary
    }

