from fastapi import FastAPI as fapi
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = fapi()

app.mount("/assets",
          StaticFiles(directory=Path(
              __file__).parent.parent.absolute() / "digitbraindttapi/assets"),
          name="assets")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/updateall")
async def updateall():
    pass


@app.get("/getexistingsolution")
async def getexistingsolution():
    pass
