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

def getJsonNamedRange(namedRange):
    '''
    Запрос на поиск именного запроса по его имени

    :param namedRange: имя Именованного диапозона
    :return: возвращает часть реквеста, а именно диапозон
    '''
    try:
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=namedRange).execute()
        print(result)
    except :
        result = {"range": -1}
    return result["range"]

if __name__ == '__main__':
    # TESTING
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheetList = spreadsheet.get('sheets')

    ss = ls.Lots(sheetList)

    #pprint(ss.spreadsheetsIds)

    range_name = "DCollect1"

    #results = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": ss.prepareLot(sheetList, 158683993, participants= 1, rangeName = range_name)}).execute()
    #results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, body= ss.prepareBody(ss.spreadsheetsIds["TestList"][0])).execute()

    result = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": ss.changeList(sheetList, 662031387, range_name, getJsonNamedRange(range_name))}).execute()
