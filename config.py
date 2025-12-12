from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class AppConfig:
    seed_dir: str = "seed"
    db_path: str = os.path.join("seed", "ops_command_center.sqlite3")

    openrouter_key: str = os.getenv("OPENROUTER_API_KEY", "").strip()
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat").strip()
    openrouter_base_url: str = os.getenv(
        "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
    ).strip().rstrip("/")

CFG = AppConfig()
