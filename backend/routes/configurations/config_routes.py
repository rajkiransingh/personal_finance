import json
import os

from fastapi import APIRouter

from utilities.common.app_config import config

logger = config.setup_logger("api.routes.config")
router = APIRouter(prefix="/config", tags=["config"])


# Get all the data related to mera paisa dashboard
@router.get("/portfolio-config")
async def get_portfolio_config():
    path = "./frontend/portfolio-config.json"
    if not os.path.exists(path):
        return {"error": f"Config not found at path: {path}"}
    with open(path) as f:
        data = json.load(f)
    return data


@router.post("/portfolio-config")
async def update_config(request: dict):
    path = "./frontend/portfolio-config.json"
    if not os.path.exists(path):
        return {"error": f"Config not found at path: {path}"}
    with open(path, "w") as f:
        json.dump(request, f, indent=2)
    return {"status": "success", "updated": "portfolio-config.json"}


# Get all the data related to mera paisa dashboard
@router.get("/stock-picking-strategy-config")
async def get_stock_strategy_config():
    path = "./frontend/stock-score-config.json"
    if not os.path.exists(path):
        return {"error": f"Config not found at path: {path}"}
    with open(path) as f:
        data = json.load(f)
    return data


@router.post("/stock-picking-strategy-config")
async def update_stock_strategy_config(request: dict):
    path = "./frontend/stock-score-config.json"
    if not os.path.exists(path):
        return {"error": f"Config not found at path: {path}"}
    with open(path, "w") as f:
        json.dump(request, f, indent=2)
    return {"status": "success", "updated": "stock-score-config.json"}


# Get all the environment data related to mera paisa dashboard
@router.get("/environment-config")
async def get_environment_config():
    protected_keys = {"DATABASE_URL", "REDIS_HOST", "REDIS_PORT"}
    path = "./.env"
    if not os.path.exists(path):
        return {"error": f"Config not found at path: {path}"}

    env_dict = {}
    with open(path) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                if key not in protected_keys:
                    env_dict[key] = value

    return env_dict


@router.post("/environment-config")
async def update_environment_config(request: dict):
    path = "./.env"
    protected_keys = ["DATABASE_URL", "REDIS_HOST", "REDIS_PORT"]

    # Load the current .env so we preserve keys not in payload
    current_env = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    current_env[key.strip()] = value.strip().strip('"').strip("'")

    # Update only keys that are provided in payload
    for k, v in request.items():
        if k not in protected_keys:
            current_env[k] = v

    # Write back to .env
    with open(path, "w") as f:
        for k, v in current_env.items():
            f.write(f"{k}={v}\n")

    return {"status": "success", "updated": len(request)}
