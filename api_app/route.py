
from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
import json

from main import functionlocationgoogle

app = FastAPI()

JSON_FILE = Path(__file__).resolve().parent / "companies.json"


class LocationRequest(BaseModel):
    location: str
    name: str


@app.post("/postlocation/")
def functionroute(request: LocationRequest):
    search_input = " ".join(
        value.strip()
        for value in (request.location, request.name)
        if value.strip()
    )

    result = functionlocationgoogle(search_input)

    return {"success": True, "data": result}


def functiongetextraction():
    if not JSON_FILE.exists():
        return {"total": 0, "businesses": []}

    with open(JSON_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


@app.get("/getcompanies/")
def functiongetcompanies():
    result = functiongetextraction()
    return {"success": True, "data": result}
