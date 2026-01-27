import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

LAST_MESSAGES_FILE = BASE_DIR / "last_messages.json"
REMINDER_SETTINGS_FILE = BASE_DIR / "reminder_settings.json"


def load_json(path: Path, cast_key=int):
    if not path.exists():
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 🛡 защита: JSON должен быть dict
        if not isinstance(data, dict):
            logger.error(f"{path.name} is not a dict")
            return {}

        casted = {cast_key(k): v for k, v in data.items()}

        # 📊 логируем успешную загрузку
        logger.info(f"Loaded {len(casted)} records from {path.name}")

        return casted

    except Exception as e:
        logger.error(f"Failed to load {path.name}: {e}")
        return {}


def save_json(path: Path, data: dict):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save {path}: {e}")

