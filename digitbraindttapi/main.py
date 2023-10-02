from fastapi import FastAPI as fapi
from fastapi import Request, status, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from getdata import GetData
from fastapi.encoders import jsonable_encoder
import time
import json

import asyncio

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

    dp_params = {'taskurl': fmData['Taurl'], 'toolsurl': fmData['Tourl'], 'machinesurl': fmData['Maurl']}
    await getdata.fetchEndpoint('http://dtpprocessingservice:3000/updateparams', dp_params)
    
    sol_params = {'pom': fmData['pom'], 'solsize': fmData['sols']}
    await getdata.fetchEndpoint('http://solgeneratorservice:3001/updateparams', sol_params)

    sch_params = {'gen': fmData['gen'], 'murate': fmData['mutrate'], 'muflip': fmData['mutflip'], 'sysdate': fmData['sysdatetime'], 'flagall': fmData['schedulallflag'], 'macount': fmData['machcount']}
    await getdata.fetchEndpoint('http://secgeneratorservice:3002/updateparams', sch_params)

    return RedirectResponse(url=app.url_path_for("root"), status_code=status.HTTP_303_SEE_OTHER)

@app.get("/updateall", response_class=HTMLResponse)
async def updateall(request: Request):
    return templates.TemplateResponse("loading.html", {"request": request})

@app.get("/getexistingsolution")
async def getexistingsolution():
    data = await getdata.fetchEndpoint('http://secgeneratorservice:3002/machinetasks')

    return data

async def s_msg(ws, conn):
    data = await ws.receive_json()
    for uid, ws in connections.items():
        if uid != "DTT":
            await ws.send_json(data)


connections = {}
@app.websocket("/wsinfo/{client_id}")
async def wsinfo(ws: WebSocket, client_id):
    await ws.accept()
    connections[client_id] = ws
    try:
        while True:
            send_task = asyncio.create_task(s_msg(ws, connections))

            done, pending = await asyncio.wait(
                {send_task},
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()
            for task in done:
                task.result()
    except WebSocketDisconnect:
        if client_id == "DTT":
            del connections[client_id]

        for uid, ws in connections.items():
            await ws.close()
        connections.clear()

#@app.get("/updateexistingsolution")
#async def updateexistingsolution():
#    return {'message': "Need to write logic!"}
