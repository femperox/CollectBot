from pprint import pprint
import httplib2
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
import re


import GoogleTabsApi.Cells_Editor as ce
import GoogleTabsApi.Spreadsheets.LotSpreadsheet as ls
import VkInterface as vk

from GoogleTabsApi.Styles.Borders import Borders as b


# Service-объект, для работы с Google-таблицами
CREDENTIALS_FILE = r'./GoogleTabsApi/creds.json'  # имя файла с закрытым ключом
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                       ['https://www.googleapis.com/auth/spreadsheets',
                                                                        'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = discovery.build('sheets', 'v4', http=httpAuth)

# id гугл таблицы
spreadsheet_id = '1A9cULhz1UAE0OWpIZ7q056NvCJj8d3Ju6C1nq2hElKc'

def getJsonNamedRange(namedRange, typeCalling = 0):
    '''
    Запрос на поиск именного запроса по его имени

    :param namedRange: имя Именованного диапозона
    :param typeCalling: тип вызова. 0 - получить только диапозон, 1 - получить полную инфу о диапозоне
    :return: возвращает часть реквеста, а именно диапозон
    '''
    try:
       result = service.spreadsheets().values().get(spreadsheetId= spreadsheet_id, range=namedRange, valueRenderOption = "FORMULA").execute()
    except :
       result = {"range": -1}

    if typeCalling == 0 : return result["range"]
    else: return result


def getSheetListProperties():
        '''

        :return: Возвращает информацию о листах
        '''

        spreadsheet = service.spreadsheets().get(spreadsheetId = spreadsheet_id).execute()
        return spreadsheet.get('sheets')

def getImageURLFromNamedRange(namedRange):
        '''
        Находит URL изображения, использованного в лоте, по информации об именованном диапозоне

        :param namedRange: имя Именованного диапозона
        :return: возвращает URL изображения
        '''

        imgUrl = getJsonNamedRange(namedRange, typeCalling = 1)
        imgUrl = imgUrl['values'][1][0]
        imgUrl = re.findall(r'"(\S+)"', imgUrl)
        imgUrl = imgUrl[0]

        return imgUrl

def createTable(spId, namedRange, participants = 1, image = "https://i.pinimg.com/originals/50/d8/03/50d803bda6ba43aaa776d0e243f03e7b.png"):
        '''
        Создаёт и заполняет базовую таблицу по заданным параметрам

        :param spId:
        :param namedRange: имя Именованного диапозона
        :param participants:
        :return:
        '''
        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                           body={"requests": ss.prepareLot(getSheetListProperties, spId, participants=participants, rangeName=namedRange)}).execute()

        service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                    body=ss.prepareBody(spId, image, collect= namedRange)).execute()

def updateTable(namedRange, request):
        '''
        Обновляет таблицу в соотвествии с информацией об участниках

        :param namedRange: имя Именованного диапозона
        :param request:
        :return:
        '''

        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                           body={"requests": ss.updateBaseOfLot(getJsonNamedRange(namedRange), request["participants"])}).execute()

        service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                    body=ss.updateBaseValues(getJsonNamedRange(namedRange),request["participantList"])).execute()

def moveTable(sheetTo, namedRange):
        '''
        Перемещает таблицу на другое место

        :param sheetTo: айди листа, на который нужно переместить таблицу
        :param namedRange: имя Именованного диапозона
        :return:
        '''

        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                           body={ "requests": ss.changeList(getSheetListProperties(), sheetTo, namedRange, getJsonNamedRange(namedRange))}).execute()

def testingCreation(spId, namedRange, lots = 1):

        for i in range(lots):
            createTable(spId, namedRange + str(i+1), i+1)

if __name__ == '__main__':
    # TESTING

    ss = ls.Lots(getSheetListProperties())

    pprint(ss.spreadsheetsIds)

    pList = []
    pList.append(([1, 2], "Name1"))
    pList.append(([3], "Name2"))

    request = \
        { "participants" : len(pList),
          "participantList": pList
        }

    vk_sample = vk.BoardBot()
    g= vk_sample.get_active_comments_users_list("https://vk.com/wall-200887174_7861")
    pprint(g)

    g = vk_sample.post_comment("Лоты и индивидуалки","test", img_urls= ["http://daurzapoved.com/images/article_images/did_you_know/daurskaya.jpg", "https://sun9-39.userapi.com/impg/ajkj3u5Wd6oBZJqPSXAy7kPWeRECSx1FIOoIXg/33j-WkLDfNA.jpg?size=1200x900&quality=96&sign=fc892e13127630e5be40a677ee264ec9&type=album"])