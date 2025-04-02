from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()

client = MongoClient("mongodb://localhost:27017/")
db = client["map_coords"]

nb_accident = 1585 + 56

class ZoneRequest(BaseModel):
    zone_ids: list[str]

@app.post("/accidents_per_zone")
async def get_accidents_per_zone(request: ZoneRequest):
    try:
        # Fetch collections
        zones_collection = db["zones"]
        routes_collection = db["routes"]

        # Calculate accidents per route
        total_routes = routes_collection.count_documents({})
        if total_routes == 0:
            raise HTTPException(status_code=400, detail="No routes found in the database.")
        accidents_per_route = nb_accident / total_routes

        # Prepare response
        response = {"zones": []}
        for zone_id in request.zone_ids:
            zone = zones_collection.find_one({"zoneId": zone_id})
            if not zone:
                response["zones"].append({"zoneId": zone_id, "accidents": "Zone not found"})
                continue

            num_routes_in_zone = len(zone.get("routes", []))
            accidents_in_zone = accidents_per_route * num_routes_in_zone
            response["zones"].append({"zoneId": zone_id, "accidents": accidents_in_zone})

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009)