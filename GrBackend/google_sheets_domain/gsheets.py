import datetime

import gspread
from google.oauth2.service_account import Credentials

from src.config import SCOPES, SERVICE_ACCOUNT_FILE, SPREADSHEET_NAME, WORKSHEET_NAME
from utils.logger import logger


class GSheetsService:
    def __init__(self) -> None:
        try:
            credentials = Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES
            )
            self.client = gspread.authorize(credentials)
        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            logger.error(
                "Make sure your SERVICE_ACCOUNT_FILE path is correct"
                " and the API is enabled."
            )
            raise e

    def store_prompt_in_sheet(self, prompt: str) -> None:
        try:
            spreadsheet = self.client.open(SPREADSHEET_NAME)
            worksheet = spreadsheet.worksheet(WORKSHEET_NAME)

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            worksheet.append_row([prompt, timestamp])
            logger.info(f"Successfully stored: '{prompt}' in Google Sheet.")
        except gspread.exceptions.SpreadsheetNotFound:
            logger.error(f"Error: Spreadsheet '{SPREADSHEET_NAME}' not found.")
            logger.error(
                "Make sure the spreadsheet name is correct "
                "and shared with the service account."
            )
        except gspread.exceptions.WorksheetNotFound:
            logger.error(
                f"Error: Worksheet '{WORKSHEET_NAME}' not found in '{SPREADSHEET_NAME}'"
            )
        except Exception as e:
            logger.error(f"An error occurred while writing to Google Sheet: {e}")
            raise e
