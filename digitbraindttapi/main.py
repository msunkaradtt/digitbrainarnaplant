from fastapi import FastAPI as fapi
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from getdata import GetData

import threading

import websocket
import json

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
        
def on_message(ws, message):
    response = json.loads(message)
    print(response["message"])

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

@app.get("/update", response_class=HTMLResponse)
async def update(request: Request):
    data = await getdata.fetchEndpoint('http://dtpprocessingservice:3000/')
    if(data['message'] == "Done"):
        data = await getdata.fetchEndpoint('http://solgeneratorservice:3001/')
        if(data['message'] == "Done"):
            ws = websocket.WebSocketApp("ws://secgeneratorservice:3002/wslearn", on_message=on_message, on_close=on_close)
            wst = threading.Thread(target=ws.run_forever)
            wst.daemon = True
            wst.start()
            #await ws.run_forever()
            return templates.TemplateResponse("loading.html", {"request": request}) 
        else:
            data = {"message": "Failed"}
    else:
        data = {"message": "Failed"}

    return data

@app.get("/updateall", response_class=HTMLResponse)
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
