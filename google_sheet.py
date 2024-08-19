import json
import os

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()


class GoogleSheet:
    def __init__(self, data):
        self.spreadsheet_id = os.getenv("SPREADSHEET_ID")
        self.range_name = os.getenv("RANGE_NAME")
        self.data = data
        self.values = [
            ["Название", "Ссылка", "Город", "Специальность", "Минимальная зарплата", "Максимальная зарплата"]
        ]

    @staticmethod
    def get_creds():
        with open('credentials.json') as f:
            credentials_info = json.load(f)

        creds = Credentials.from_service_account_info(credentials_info,
                                                      scopes=['https://www.googleapis.com/auth/spreadsheets'])
        return creds

    def clear_sheet(self, creds):
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        body = {}
        result = sheet.values().clear(spreadsheetId=self.spreadsheet_id, range=self.range_name, body=body).execute()
        return result

    def write_to_google_sheet(self, creds):
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        body = {
            'values': self.values
        }
        result = sheet.values().update(spreadsheetId=self.spreadsheet_id, range=self.range_name, valueInputOption='RAW',
                                       body=body).execute()
        return result

    def get_values(self):
        for item in self.data["items"]:
            result = [
                item.get("name"),
                item.get("alternate_url"),
                item.get("area", {}).get("name"),
                item.get("professional_roles", [{}])[0].get("name"),
                (item.get("salary") or {}).get("from", ''),
                (item.get("salary") or {}).get("to", '')
            ]
            self.values.append(result)

        creds = self.get_creds()
        self.clear_sheet(creds)
        self.write_to_google_sheet(creds)



