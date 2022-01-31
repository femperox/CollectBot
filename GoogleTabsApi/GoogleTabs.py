from pprint import pprint
import httplib2
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
import re
from operator import itemgetter

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

           # Когда позицию никто не взял
           try:
               participantList.append([str(info[i][0]), info[i][1]])
           except:
               participantList.append([str(info[i][0]), ''])
           i += 1

       return participantList


    def createTable(self, spId, namedRange, participants = 1, item = [], image = "https://i.pinimg.com/originals/50/d8/03/50d803bda6ba43aaa776d0e243f03e7b.png"):
        '''
        Создаёт и заполняет базовую таблицу по заданным параметрам

        :param spId: айди листа в таблице
        :param namedRange: имя Именованного диапозона
        :param participants: количество участников лота
        :param item:
        :param image: ссылка на изображение для оформления лота
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
        :param request: словарь участников лота вида: {"participants": количество, "participantList": [[ строка_позиций, участник], ...] }
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

        self.__service.spreadsheets().values().batchUpdate(spreadsheetId=self.__spreadsheet_id,
                                                           body=self.sp.setDateOfShipment(sheetTo, self.getJsonNamedRange(namedRange))).execute()

    def addRows(self, spId):
        '''
        Добавление строчек на лист
        :param spId: айди листа в таблице
        :return:
        '''

        self.__service.spreadsheets().batchUpdate(spreadsheetId=self.__spreadsheet_id,
                                                  body={"requests": [ce.updateSheetProperties(spId, 650)]}).execute()


    def makeItemString(self, items):
        '''
        Создаёт упорядоченную по номерам позций строку айтомов
        :param items: массив айтемов
        :return: возвращает строку
        '''


        items = [int(item) for item in items]
        items.sort()
        itemString = (''.join([str(item)+', ' for item in items]))[0:-2]

        return itemString


    def getTopicUrl(self, spId, namedRange):
        '''
        Получение ссылки из обсуждения на конкретный лот
        :param spId: айди листа в таблице
        :param namedRange: имя Именованного диапозона
        :return: строка со ссылкой
        '''

        topicUrl = self.getJsonNamedRange(namedRange, typeCalling=1)['values'][2][-1]
        topicUrl = re.findall('"(\S+)"', topicUrl)[0]

        return topicUrl

    def changePositions(self, spId, namedRange, newParticipants):
        '''
        Производит автоматическую перепись позиций для участников лота (новые участники включаются)
        :param spId: айди листа в таблице
        :param namedRange: имя Именованного диапозона
        :param newParticipants: список участников и их новых позиций в формате [[ строка_позиций, участник], ...]
        :return:
        '''

        oldParticipants = self.getParticipantsList(spId, namedRange)
        actualParticipants = []

        activeIndexes = set()

        for new in newParticipants:

            # связка хохяин - индекс
            oldParticipantsNoItems = {part[1]: oldParticipants.index(part) for part in oldParticipants}
            actualParticipantsNoItems = {part[1] : actualParticipants.index(part) for part in actualParticipants}

            newItems = new[0].split(', ')

            for i in range(len(oldParticipants)):

               oldItems = oldParticipants[i][0].split(', ')

               for newItem in newItems:
                  if newItem in oldItems:

                       if len(oldParticipants[i][0]) > 1:

                            oldItems.remove(newItem)
                            oldParticipants[i][0] = self.makeItemString(oldItems)

                            if oldParticipants[i][1] in actualParticipantsNoItems.keys():
                               index = actualParticipantsNoItems[oldParticipants[i][1]]
                               actualParticipants[index][0] = oldParticipants[i][0]
                            else:
                                actualParticipants.append(oldParticipants[i])
                       activeIndexes.add(i)

            # заполняем данными человека, которому уступили
            if new[1] in oldParticipantsNoItems.keys():
                index = oldParticipantsNoItems[new[1]]
                itemList = oldParticipants[index][0].split(', ')
                itemList.extend(newItems)
                activeIndexes.add(index)
            else: itemList = newItems

            if new[1] in actualParticipantsNoItems.keys():
                index = actualParticipantsNoItems[new[1]]
                actualParticipants[index][0] = self.makeItemString(itemList)
            else:
                actualParticipants.append([self.makeItemString(itemList), new[1]])

        # позиции тех, у которых ничего неизменилось
        inactiveIndexes = set([i for i in range(len(oldParticipants))]) - activeIndexes
        inactiveParticipants = [oldParticipants[i] for i in inactiveIndexes]
        actualParticipants.extend(inactiveParticipants)


        # зачистка от пустых позиций
        act = actualParticipants.copy()
        for i in range(len(actualParticipants)):
            if len(actualParticipants[i][0]) == 0:
                act.remove(actualParticipants[i])
        actualParticipants = act

        actualParticipants.sort(key = lambda x: x[0].find(',') > 0 and int(x[0][0:x[0].find(',')]) or int(x[0][0:len(x[0])]))


        request = { "participants": len(actualParticipants),
                    "participantList": actualParticipants
        }

        self.updateTable(namedRange, request, self.getTopicUrl(spId, namedRange))





class TestingGoogleTabs(GoogleTabs):

    def testingCreation(self, spId, namedRange, lots = 1):

        for i in range(lots):
            self.createTable(spId, namedRange + str(i+1), i+1)




