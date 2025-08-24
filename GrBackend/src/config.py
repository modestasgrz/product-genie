import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

IS_DEBUG = os.getenv("GRADIO_DEBUG", "True") == "True"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8030"))
SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")  # old: "987654"
BLENDER_APP = os.getenv("BLENDER_APP")
BLENDER_SCRIPT_FILE = os.getenv("BLENDER_SCRIPT_FILE")
BLEND_BASE_FILE = os.getenv("BLENDER_BASE_FILE")
BLENDER_FUNCTION_NAME = "process"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

MESHY_API_KEY = os.getenv("MESHY_API_KEY")
MESHY_BASE_URL = os.getenv("MESHY_BASE_URL", "https://api.meshy.ai/openapi/v1")
MESHY_AI_TIMEOUT = float(os.getenv("MESHY_AI_TIMEOUT", "60.0"))

D_PRESSO_API_KEY = os.getenv("D_PRESSO_API_KEY")
D_PRESSO_BASE_URL = os.getenv(
    "D_PRESSO_BASE_URL", "https://api.3dpresso.ai/prod/api/v2"
)
D_PRESSO_TIMEOUT = float(os.getenv("D_PRESSO_TIMEOUT", "60.0"))

# --- Google Spreadsheets ---------
# --- Configuration ---
# Replace with the path to your downloaded service account JSON file
SERVICE_ACCOUNT_FILE = (
    Path(__file__).parent.parent / "gemini-api-lithuania-c7acb5367248.json"
)
SPREADSHEET_NAME = "Product Genie - Prompts"  # The exact name of your Google Sheet
WORKSHEET_NAME = "Prompts"  # The name of the specific sheet/tab within your spreadsheet

# --- Authentication ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]  # Drive scope for finding sheets

# --- GCP Configuration ---
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_ZONE = os.getenv("GCP_ZONE", "europe-central2-a")
GCP_MACHINE_TYPE = os.getenv("GCP_MACHINE_TYPE", "e2-standard-2")
GCP_CONTAINER_IMAGE = os.getenv("GCP_CONTAINER_IMAGE")
GCP_SERVICE_ACCOUNT_EMAIL = os.getenv("GCP_SERVICE_ACCOUNT_EMAIL", "default")
RENDER_ENVIRONMENT = os.getenv("RENDER_ENVIRONMENT", "local")  # 'local' or 'gcp'
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
GCP_VM_MAX_RUN_DURATION_SECONDS = int(
    os.getenv("GCP_VM_MAX_RUN_DURATION_SECONDS", "3600")
)

