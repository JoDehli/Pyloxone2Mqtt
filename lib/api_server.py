from starlette.requests import Request

from fastapi import FastAPI, Depends
from starlette.staticfiles import StaticFiles

from lib.app.models import Device, Room, Category
from lib.event_bus import EventBus
from fastapi.templating import Jinja2Templates

app = FastAPI()
# Mount static files (CSS, JS, images, etc.)
app.mount("/static", StaticFiles(directory="lib/app/static"), name="static")
# Set up templates
templates = Jinja2Templates(directory="lib/app/templates")

def generate_data_for_frontend(structure_file:dict):
    data = {}
    software_version = ".".join(map(str, structure_file["softwareVersion"]))
    data.update({"software_version": software_version})

    controls = []
    rooms = {}
    cats = {}

    for _ in structure_file["rooms"]:
        room = structure_file["rooms"][_]
        rooms[room["uuid"]] = Room(room["name"], room["uuid"])

    for _ in structure_file["cats"]:
        cat = structure_file["cats"][_]
        cats[cat["uuid"]] = Category(cat["name"], cat["uuid"])

    for c in structure_file["controls"]:
        device = Device(structure_file["controls"][c]["type"],
                        structure_file["controls"][c]["name"],
                        rooms[structure_file["controls"][c]["room"]],
                        cats[structure_file["controls"][c]["cat"]],
                        )
        controls.append(device)

    data.update({"controls": controls})

    return data

@app.get("/")
async def read_root(request: Request, event_bus: EventBus = Depends()):
    data = generate_data_for_frontend(event_bus.structure_file)
    return templates.TemplateResponse("index.html", {"request": request,"title": "PyLoxone2Mqtt", "structure_file_data": data})

def run_fastapi_app(event_bus):
    import uvicorn
    app.dependency_overrides[EventBus] = lambda: event_bus
    uvicorn.run(app, host="0.0.0.0", port=8000)