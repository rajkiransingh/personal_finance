# ===============================================================
# 📂 Config Handlers
# ===============================================================
import json
from typing import Dict, Any


def load_config(path: str = "portfolio_config.json") -> Dict[str, Any]:
    with open(path, "r") as f:
        return json.load(f)


def save_config(cfg: Dict[str, Any], path: str = "portfolio_config.json"):
    with open(path, "w") as f:
        json.dump(cfg, f, indent=2)
