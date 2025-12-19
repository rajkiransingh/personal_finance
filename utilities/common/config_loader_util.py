# ===============================================================
# 📂 Config Handlers
# ===============================================================
import json
from typing import Dict, Any


def load_config(path: str = "portfolio_config.json") -> Dict[str, Any]:
    """Load portfolio configuration from JSON file.

    Args:
        path: Path to the configuration JSON file

    Returns:
        Dictionary containing portfolio configuration
    """
    with open(path, "r") as f:
        return json.load(f)


def save_config(cfg: Dict[str, Any], path: str = "portfolio_config.json"):
    """Save portfolio configuration to JSON file.

    Args:
        cfg: Configuration dictionary to save
        path: Path to the configuration JSON file
    """
    with open(path, "w") as f:
        json.dump(cfg, f, indent=2)
