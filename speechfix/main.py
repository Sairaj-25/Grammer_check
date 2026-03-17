from fastapi import FastAPI, Request
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="SpeechFix API")

BASE_DIR = Path(__file__).resolve().parent
# Mount the static directory
app.mount(
    "/speechfix/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static"
)

# setup templates directory
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# root endpoint to return the html template
@app.get("/")
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "score": 0})
