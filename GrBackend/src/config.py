import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

IS_DEBUG = os.getenv("GRADIO_DEBUG", "True") == "True"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "7860"))
SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")  # old: "987654"
BLENDER_APP = os.getenv("BLENDER_APP")
BLENDER_SCRIPT_FILE = os.getenv("BLENDER_SCRIPT_FILE")
BLEND_BASE_FILE = os.getenv("BLENDER_BASE_FILE")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
