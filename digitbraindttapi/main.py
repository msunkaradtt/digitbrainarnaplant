from fastapi import FastAPI as fapi
from fastapi import Request, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
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


@app.get("/updateall")
async def updateall(request: Request, background_task: BackgroundTasks):
    background_task.add_task(update_all_async)

    return templates.TemplateResponse("loading.html", {"request": request})


@app.get("/updateexistingsolution")
async def updateexistingsolution():
    return {'message': "Need to write logic!"}


@app.get("/getexistingsolution")
async def getexistingsolution():
    data = await getdata.fetchEndpoint('http://secservice:3002/machinetasks')

    return data


async def update_all_async():
    res_dpservice = await getdata.fetchEndpoint('http://dpservice:3000')

    res_solservice = None
    if res_dpservice:
        res_solservice = await getdata.fetchEndpoint('http://solservice:3001')

    if res_dpservice and res_solservice:
        _ = await getdata.fetchEndpoint('http://secservice:3002')