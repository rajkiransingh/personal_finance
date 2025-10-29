import json
import logging
import os

from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/config", tags=["config"])


# Get all the data related to mera paisa dashboard
@router.get("/portfolio-config")
async def get_portfolio_config():
    path = f"./frontend/portfolio-config.json"
    if not os.path.exists(path):
        return {"error": f"Config not found at path: {path}"}
    with open(path) as f:
        data = json.load(f)
    return data


@router.post("/portfolio-config")
async def update_config(request: dict):
    path = f"./frontend/portfolio-config.json"
    if not os.path.exists(path):
        return {"error": f"Config not found at path: {path}"}
    with open(path, "w") as f:
        json.dump(request, f, indent=2)
    return {"status": "success", "updated": "portfolio-config.json"}


# Get all the data related to mera paisa dashboard
@router.get("/stock-picking-strategy-config")
async def get_portfolio_config():
    path = f"./frontend/stock-score-config.json"
    if not os.path.exists(path):
        return {"error": f"Config not found at path: {path}"}
    with open(path) as f:
        data = json.load(f)
    return data


@router.post("/stock-picking-strategy-config")
async def update_config(request: dict):
    path = f"./frontend/stock-score-config.json"
    if not os.path.exists(path):
        return {"error": f"Config not found at path: {path}"}
    with open(path, "w") as f:
        json.dump(request, f, indent=2)
    return {"status": "success", "updated": "stock-score-config.json"}


# Get all the environment data related to mera paisa dashboard
@router.get("/environment-config")
async def get_environment_config():
    path = f"./.env"
    if not os.path.exists(path):
        return {"error": f"Config not found at path: {path}"}
    with open(path) as f:
        data = json.load(f)
    return data


@router.post("/environment-config")
async def update_environment_config(request: dict):
    path = f"./.env"
    if not os.path.exists(path):
        return {"error": f"Config not found at path: {path}"}
    with open(path, "w") as f:
        json.dump(request, f, indent=2)
    return {"status": "success", "updated": "environment-config.json"}
