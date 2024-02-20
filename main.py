from fastapi import FastAPI, Request, BackgroundTasks
from starlette.templating import Jinja2Templates
import json
import requests
import asyncio, datetime

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Global variables
headers = {
    'Accept': 'application/json, text/javascript',
    'Accept-Language': 'es-419,es;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://www.montevideo.gub.uy',
    'Referer': 'https://www.montevideo.gub.uy/buses/mapaBuses.html',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

bus_line = ""
coordinates_list = []

@app.get("/")
async def get_map(request: Request):
    global coordinates_list
    global bus_line
    coordinates_list = []
    bus_line = ""
    return templates.TemplateResponse("map.html", {"request": request, "coordinates_list": json.dumps(coordinates_list) })

@app.post("/map")
async def update_coordinates(request: Request, background_tasks: BackgroundTasks):
    global bus_line
    #global coordinates_list
    form_data = await request.form()
    bus_line = str(form_data.get("coordinates"))
    background_tasks.add_task(refresh_coordinates)

    coordinates_list = await request_method(bus_line)
    print("Coordinates: " + bus_line + ": ", coordinates_list)
    return templates.TemplateResponse("map.html", {"request": request, "coordinates_list": json.dumps(coordinates_list) })

async def refresh_coordinates():
    global coordinates_list
    while True:
        await asyncio.sleep(15)
        coordinates_list = await request_method(bus_line)

async def request_method(bus_line):
    coordinatesList = []

    if bus_line != "":
    
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("REFRESH: " + bus_line + " - "+ current_time)
        
        json_data = {
            'subsistema': '-1',
            'empresa': '-1',
            'lineas': [str(bus_line)],
        }

        response = requests.post('https://www.montevideo.gub.uy/buses/rest/stm-online',  headers=headers, json=json_data)

        if response.status_code == 200:
            resp = response.json()
            for feature in resp["features"]:
                
                destinoDesc = feature["properties"]["destinoDesc"]
                coordinates = feature["geometry"]["coordinates"]
                coordinates.reverse()  # Switch the order of the coordinates
                properties = [str(bus_line) + " - Destino: "+destinoDesc] + coordinates
                coordinatesList.append(properties)

        else:
            print(response.status_code)

    return coordinatesList


from fastapi.responses import JSONResponse

@app.get("/coordinates")
async def get_coordinates():
    return JSONResponse(content=coordinates_list)