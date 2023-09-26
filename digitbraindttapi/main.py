from fastapi import FastAPI as fapi
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from getdata import GetData
from fastapi.encoders import jsonable_encoder

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

@app.get("/settings", response_class=HTMLResponse, include_in_schema=False)
async def updateSettings(request: Request):
    dp_data = await getdata.fetchEndpoint('http://dtpprocessingservice:3000/parameters')
    sol_data = await getdata.fetchEndpoint('http://solgeneratorservice:3001/parameters')
    sch_data = await getdata.fetchEndpoint('http://secgeneratorservice:3002/parameters')
    return templates.TemplateResponse("settings.html", {"request": request, "data_p": dp_data, "data_so": sol_data, "data_sc": sch_data})

@app.post("/settings", include_in_schema=False)
async def updateSettings(request: Request):
    fmData = await request.form()
    fmData = jsonable_encoder(fmData)
    print(fmData)
    return fmData

@app.get("/updateall", response_class=HTMLResponse)
async def updateall(request: Request):
    return templates.TemplateResponse("loading.html", {"request": request})

@app.get("/getexistingsolution")
async def getexistingsolution():
    data = await getdata.fetchEndpoint('http://secgeneratorservice:3002/machinetasks')

    return data

#@app.get("/updateexistingsolution")
#async def updateexistingsolution():
#    return {'message': "Need to write logic!"}
