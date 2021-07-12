from pprint import pprint
import httplib2
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

import GoogleTabsApi.Cells_Editor as ce
import GoogleTabsApi.Spreadsheets.LotSpreadsheet as ls

from GoogleTabsApi.Styles.Borders import Borders as b

#Service-объект, для работы с Google-таблицами
CREDENTIALS_FILE = r'./GoogleTabsApi/creds.json'  # имя файла с закрытым ключом

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                                                                                  'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = discovery.build('sheets', 'v4', http = httpAuth)

# id гугл таблицы
spreadsheet_id = '1A9cULhz1UAE0OWpIZ7q056NvCJj8d3Ju6C1nq2hElKc'

if __name__ == '__main__':
    # TESTING
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheetList = spreadsheet.get('sheets')

    ss = ls.Lots(sheetList)

    #pprint(ss.spreadsheetsIds)

    results = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": ss.prepareLot(sheetList, 158683993, participants= 1)}).execute()
    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, body= ss.prepareBody(ss.spreadsheetsIds["Test"][0])).execute()
