
from fastapi import FastAPI, Request
from starlette.templating import Jinja2Templates
import json, requests


app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/map")
async def get_map(request: Request):
    # Example coordinates list
    coordinates_list = [
        ["7C6B07", -34.88996, -56.194386],
    ]

    return templates.TemplateResponse("map.html", {"request": request, "coordinates_list": json.dumps(coordinates_list) })

@app.post("/update_coordinates")
async def update_coordinates(request: Request):
    # Get number from form data
    form_data = await request.form()
    number = int(form_data.get("coordinates"))

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

    json_data = {
        'subsistema': '-1',
        'empresa': '-1',
        'lineas': [
            str(number),
        ],
    }

    response = requests.post('https://www.montevideo.gub.uy/buses/rest/stm-online', headers=headers, json=json_data)
    
    if response.status_code == 200:

        resp = response.json()

        coordinatesList = []

        for feature in resp["features"]:
            sublinea = feature["properties"]["sublinea"]
            coordinates = feature["geometry"]["coordinates"]
            coordinates.reverse()  # Switch the order of the coordinates
            properties = [str(number) + " - "+sublinea] + coordinates
            coordinatesList.append(properties)
    
        # Update the latitude and longitude values
        return templates.TemplateResponse("map.html", {"request": request, "coordinates_list": json.dumps(coordinatesList) })
    else:
        return {"message": "Failed to update coordinates."}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)