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
    except :
        result = {"range": -1}
    return result["range"]

def getSheetListProperties():
    '''

    :return:
    '''

    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    return spreadsheet.get('sheets')

def createTable(spId, namedRange, participants = 1):
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                       body={"requests": ss.prepareLot(getSheetListProperties(), spId, participants=participants, rangeName=namedRange)}).execute()

    service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                body=ss.prepareBody(spId)).execute()

def updateTable(namedRange, request):

    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                       body={"requests": ss.updateLot(getJsonNamedRange(namedRange), request["participants"])}).execute()

    service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                body=ss.updateValues(getJsonNamedRange(namedRange),request["participantList"])).execute()

def testingCreation(spId, namedRange, lots = 1):

    for i in range(lots):
        createTable(spId, namedRange + str(i+1), i+1)

if __name__ == '__main__':
    # TESTING

    ss = ls.Lots(getSheetListProperties())

    #pprint(ss.spreadsheetsIds)

    range_name = "DCollect"
    #testingCreation(158683993, range_name, 3)

    pList = []
    pList.append(([1, 2], "Name1"))
    pList.append(([3], "Name2"))

    request = \
        { "participants" : 2,
          "participantList": pList
        }

    r = "DCollect3"

    updateTable(r, request)


    #result = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": ss.changeList(getSheetListProperties(), 662031387, r, getJsonNamedRange(r))}).execute()
