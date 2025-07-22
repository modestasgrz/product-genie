import sys
from pathlib import Path

# Add the parent directory of GrBackend to the Python path
# This is necessary to import modules from GrBackend
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from google_sheets_domain.gsheets import GSheetsService

gsheets_service = GSheetsService()

gsheets_service.store_prompt_in_sheet(prompt="This is a test prompt")
