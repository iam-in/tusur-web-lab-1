from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "app" / "static" / "uploads"
RESULT_DIR = UPLOAD_DIR / "results"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "webp"}
MAX_CONTENT_LENGTH = 8 * 1024 * 1024
SECRET_KEY = "secret-key"
