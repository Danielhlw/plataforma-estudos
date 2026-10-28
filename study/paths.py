from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDOR_WORD_BANK = ROOT / "vendor" / "word-bank"
DATA_DIR = ROOT / "data"
PLATFORM_DB = DATA_DIR / "platform.db"
CNH_DATA = ROOT / "study" / "courses" / "cnh" / "data"
