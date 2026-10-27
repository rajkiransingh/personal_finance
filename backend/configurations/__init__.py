"""
Configurations package.
Ensures bank_config.py exists by copying from bank_config.py.example if missing.
"""
from pathlib import Path
import shutil

_CONFIG_DIR = Path(__file__).resolve().parent
_BANK_CONFIG = _CONFIG_DIR / "bank_config.py"
_EXAMPLE_CONFIG = _CONFIG_DIR / "bank_config.py.example"

if not _BANK_CONFIG.exists() and _EXAMPLE_CONFIG.exists():
    shutil.copyfile(_EXAMPLE_CONFIG, _BANK_CONFIG)
