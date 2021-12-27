from pprint import pprint
import httplib2
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
import re

import GoogleTabsApi.Cells_Editor as ce
import GoogleTabsApi.Spreadsheets.LotSpreadsheet as ls

class GoogleTabs:

    def __init__(self):
        # Service-объект, для работы с Google-таблицами
        CREDENTIALS_FILE = r'./GoogleTabsApi/creds.json'  # имя файла с закрытым ключом
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                       ['https://www.googleapis.com/auth/spreadsheets',
                                                                        'https://www.googleapis.com/auth/drive'])
        httpAuth = credentials.authorize(httplib2.Http())
        self.__service = discovery.build('sheets', 'v4', http=httpAuth)

        # id гугл таблицы
        self.__spreadsheet_id = '1A9cULhz1UAE0OWpIZ7q056NvCJj8d3Ju6C1nq2hElKc'

        self.sp = ls.Lots(self.getSheetListProperties())

    def getJsonNamedRange(self,namedRange, typeCalling = 0):
        '''
        Запрос на поиск именного запроса по его имени

        :param namedRange: имя Именованного диапозона
        :param typeCalling: тип вызова. 0 - получить только диапозон, 1 - получить полную инфу о диапозоне
        :return: возвращает часть реквеста, а именно диапозон
        '''
        try:
           result = self.__service.spreadsheets().values().get(spreadsheetId= self.__spreadsheet_id, range=namedRange, valueRenderOption ="FORMULA").execute()
        except :
           result = {"range": -1}

        if typeCalling == 0 : return result["range"]
        else: return result


    def getSheetListProperties(self):
        '''

        :return: Возвращает информацию о листах
        '''

        spreadsheet = self.__service.spreadsheets().get(spreadsheetId = self.__spreadsheet_id).execute()
        return spreadsheet.get('sheets')

    def getImageURLFromNamedRange(self, namedRange):
        '''
        Находит URL изображения, использованного в лоте, по информации об именованном диапозоне

        :param namedRange: имя Именованного диапозона
        :return: возвращает URL изображения
        '''

        imgUrl = self.getJsonNamedRange(namedRange, typeCalling = 1)
        imgUrl = imgUrl['values'][1][0]
        imgUrl = re.findall(r'"(\S+)"', imgUrl)
        imgUrl = imgUrl[0]

        return imgUrl

    def getParticipantsList(self, spId, namedRange):

       info = self.getJsonNamedRange(namedRange, typeCalling = 1)

       info = info['values'][14:]

       i = 0
       participantList = []
       while info[i][0] != "СУММАРНО":
           participantList.append((info[i][0], info[i][1]))
           i += 1

       return participantList


    def createTable(self, spId, namedRange, participants = 1, item = [], image = "https://i.pinimg.com/originals/50/d8/03/50d803bda6ba43aaa776d0e243f03e7b.png"):
        '''
        Создаёт и заполняет базовую таблицу по заданным параметрам

        :param spId:
        :param namedRange: имя Именованного диапозона
        :param participants:
        :return:
        '''
        self.__service.spreadsheets().batchUpdate(spreadsheetId=self.__spreadsheet_id,
                                                  body={"requests": self.sp.prepareLot(self.getSheetListProperties(), spId, participants=participants, rangeName=namedRange)}).execute()

        self.__service.spreadsheets().values().batchUpdate(spreadsheetId=self.__spreadsheet_id,
                                                           body=self.sp.prepareBody(spId, image, collect= namedRange, item = item)).execute()

    def updateTable(self, namedRange, request, topicUrl):
        '''
        Обновляет таблицу в соотвествии с информацией об участниках

        :param namedRange: имя Именованного диапозона
        :param request:
        :return:
        '''

        self.__service.spreadsheets().batchUpdate(spreadsheetId=self.__spreadsheet_id,
                                                  body={"requests": self.sp.updateBaseOfLot(self.getJsonNamedRange(namedRange), request["participants"])}).execute()

        self.__service.spreadsheets().values().batchUpdate(spreadsheetId=self.__spreadsheet_id,
                                                           body=self.sp.updateBaseValues(self.getJsonNamedRange(namedRange),request["participantList"], topicUrl)).execute()

    def moveTable(self, sheetTo, namedRange):
        '''
        Перемещает таблицу на другое место

        :param sheetTo: айди листа, на который нужно переместить таблицу
        :param namedRange: имя Именованного диапозона
        :return:
        '''

        self.__service.spreadsheets().batchUpdate(spreadsheetId=self.__spreadsheet_id,
                                                  body={ "requests": self.sp.changeList(self.getSheetListProperties(), sheetTo, namedRange, self.getJsonNamedRange(namedRange))}).execute()


    def addRows(self, spId):


        self.__service.spreadsheets().batchUpdate(spreadsheetId=self.__spreadsheet_id,
                                                  body={"requests": [ce.updateSheetProperties(spId, 650)]}).execute()

class TestingGoogleTabs(GoogleTabs):

    def testingCreation(self, spId, namedRange, lots = 1):

        for i in range(lots):
            self.createTable(spId, namedRange + str(i+1), i+1)




