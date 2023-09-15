from fastapi import FastAPI as fapi
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from getdata import GetData

app = fapi()
getdata = GetData()

app.mount("/assets",
          StaticFiles(directory=Path(
              __file__).parent.absolute() / "assets"),
          name="assets")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/update")
async def update():
    data = await getdata.fetchEndpoint('http://dtpprocessingservice:3000/')
    if(data['message'] == "Done"):
        data = await getdata.fetchEndpoint('http://solgeneratorservice:3001/')

    return data


@app.get("/updateall")
async def updateall(request: Request):
    return templates.TemplateResponse("loading.html", {"request": request})


@app.get("/updateexistingsolution")
async def updateexistingsolution():
    return {'message': "Need to write logic!"}


@app.get("/getexistingsolution")
async def getexistingsolution():
    # secservice
    data = await getdata.fetchEndpoint('http://secgeneratorservice:3002/machinetasks')

    return data
