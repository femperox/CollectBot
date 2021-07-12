import GoogleTabsApi.Cells_Editor as ce
from GoogleTabsApi.Styles.Borders import Borders as b
from GoogleTabsApi.Styles.Colors import Colors as c

class Lots():

 spreadsheetsIds = {}
 startLotRow = 0
 startParticipantRow = 0
 summaryRow = 0

 def __init__(self, sheetList):

   self.spreadsheetsIds['Lera'] = (sheetList[0]['properties']['sheetId'], sheetList[0]['properties']['index'], sheetList[0]['properties']['title'])
   self.spreadsheetsIds['Dasha_lot'] = (sheetList[3]['properties']['sheetId'], sheetList[3]['properties']['index'], sheetList[3]['properties']['title'])
   self.spreadsheetsIds['Dasha_ind'] = (sheetList[4]['properties']['sheetId'], sheetList[4]['properties']['index'], sheetList[4]['properties']['title'])
   self.spreadsheetsIds['Dasha_rf'] = (sheetList[5]['properties']['sheetId'], sheetList[5]['properties']['index'], sheetList[5]['properties']['title'])
   self.spreadsheetsIds['Dasha_arc'] = (sheetList[6]['properties']['sheetId'], sheetList[6]['properties']['index'], sheetList[6]['properties']['title'])
   self.spreadsheetsIds['Test'] = (sheetList[8]['properties']['sheetId'], sheetList[8]['properties']['index'], sheetList[8]['properties']['title'])


 def findFreeRaw(self, sheetList, spId):
     '''
     Поиск свободной ячейки в таблице

     :param sheetList: Список свойств листов таблицы
     :param spId: айди листа в таблице
     :return: возвращает индекс свободной строки
     '''

     spIds = list(self.spreadsheetsIds.items())

     sheetId = 0
     for i in range(len(spIds)):
         if spIds[i][1][0] == spId:
            sheetId = spIds[i][1][1]
            break

     # Поиск свободного места
     try:
        freeRaw = sorted(sheetList[sheetId]['merges'], key=lambda x: x['endRowIndex'], reverse=True)[0]['endRowIndex']  # Узнаём последнюю заполненную строчку
        return freeRaw+2
     except:
         return 1


 def prepareLot(self, sheetList, spId, participants = 1):
    '''
     подготовка json запроса для создания таблицы лота

     :param sheetList: Список свойств листов таблицы
     :param spId: айди листа в таблице
     :param participants: количество участников лота
     :return: возвращает json запрос
    '''

    request = []
    self.startLotRow = self.findFreeRaw(sheetList, spId)
    self.startParticipantRow = self.startLotRow + 14
    self.summaryRow = self.startParticipantRow + participants

    # стили ячеек
    request.append(ce.repeatCells(spId, "A{0}:G{1}".format(self.startLotRow, self.summaryRow), c.white))
    request.append(ce.repeatCells(spId, "H{0}:H{1}".format(self.startLotRow, self.startLotRow + 2), c.white, hali = "RIGHT"))
    request.append(ce.repeatCells(spId, "I{0}:I{1}".format(self.startLotRow, self.startLotRow + 2), c.white))
    request.append(ce.repeatCells(spId, "C{0}:C{0}".format(self.startLotRow), c.light_purple))
    request.append(ce.repeatCells(spId, "A{0}:B{0}".format(self.startLotRow), c.light_purple, hali = "RIGHT"))
    request.append(ce.repeatCells(spId, "A{0}:C{0}".format(self.summaryRow), c.light_purple, hali = "RIGHT"))
    request.append(ce.repeatCells(spId, "D{0}:F{0}".format(self.summaryRow), c.light_purple))

    # объдинение ячеек
    request.append(ce.mergeCells(spId, "A{0}:B{0}".format(self.startLotRow)))
    request.append(ce.mergeCells(spId, "D{0}:D{1}".format(self.startLotRow, self.startLotRow+13)))
    request.append(ce.mergeCells(spId, "E{0}:E{1}".format(self.startLotRow, self.startLotRow+13)))
    request.append(ce.mergeCells(spId, "F{0}:F{1}".format(self.startLotRow, self.startLotRow+13)))
    request.append(ce.mergeCells(spId, "G{0}:G{1}".format(self.startLotRow, self.startLotRow+13)))
    request.append(ce.mergeCells(spId, "A{0}:C{1}".format(self.startLotRow+1, self.startLotRow+13)))  # место для картинки
    request.append(ce.mergeCells(spId, "A{0}:C{0}".format(self.summaryRow))) # для "суммарно"


    for i in range(participants):
        request.append(ce.mergeCells(spId, "B{0}:C{0}".format(self.startParticipantRow+i)))
        request.append(ce.repeatCells(spId, "D{0}:E{0}".format(self.startParticipantRow+i), c.light_red))
        request.append(ce.repeatCells(spId, "G{0}:G{0}".format(self.startParticipantRow + i), c.light_red))

    # границы ячеек
    request.append(ce.setCellBorder(spId, "A{0}:G{1}".format(self.startLotRow, self.summaryRow), bstyleList=b.plain_black))
    request.append(ce.setCellBorder(spId, "H{0}:I{1}".format(self.startLotRow, self.startLotRow+2), bstyleList=b.plain_black))
    request.append(ce.setCellBorder(spId, "H{0}:I{1}".format(self.startLotRow+3, self.summaryRow), only_outer= True, bstyleList=b.plain_black))

    return request

 def prepareValues(self, spId, collectNum = 0, collectName = "Коллективка"):
     '''
     подготовка блока data в json-запросе для заполнения таблицы значениями

     :param spId: айди листа в таблице
     :param collectNum: номер коллективки
     :param collectName: название коллективки (Коллективка/Индивидуалка)
     :return: возвращает часть json запроса
     '''

     data = []

     participants = self.summaryRow - self.startParticipantRow

     # Поиск названия листа
     spItems = list(self.spreadsheetsIds.items())
     sheetTitle = ""
     for i in range(len(spItems)):
         if spItems[i][1][0] == spId:
             sheetTitle = spItems[i][1][2]
             break

     ran = sheetTitle +"!A{0}:B{0}".format(self.startLotRow)
     data.append(ce.insertValue(spId, ran, "{1} №{0}   Трек:".format(collectNum, collectName)))

     words = ["Позиция (с налогом)", "Доставка по Япе", "Доставка до РФ", "Задолжность",
              "Вес лота:", "Беседа лота:", "Лот в обсуждении:", "СУММАРНО"]
     mergedWordsAm = 4
     unmergedWordsAm = len(words) - mergedWordsAm

     # Имена шапок по оплатам и задание формулы суммы
     for i in range(mergedWordsAm):
         letter = chr(i + 3 + ord('a'))
         ran = sheetTitle +"!{0}{1}".format(letter, self.startLotRow)
         data.append(ce.insertValue(spId, ran, words[i]))

         ran = sheetTitle + "!{0}{1}".format(letter, self.summaryRow)
         if letter == 'g':
             formula = "=SUM(D{0}:F{0})".format(self.summaryRow)
         else:
             formula = "=SUM({0}{1}:{0}{2})".format(letter, self.startParticipantRow, self.summaryRow-1)
         data.append(ce.insertValue(spId, ran, formula))

     # Имена шапок инфы о лоте
     for i in range(unmergedWordsAm-1):
         ran = sheetTitle + "!H{0}".format(self.startLotRow+i)
         data.append(ce.insertValue(spId, ran, words[mergedWordsAm+i]))

     # Нумерация участников и задание формулы задолжности
     for i in range(participants):
         ran = sheetTitle + "!A{0}".format(self.startParticipantRow+i)
         data.append(ce.insertValue(spId, ran, i+1))

         ran = ran.replace('A', 'G', 1)
         data.append(ce.insertValue(spId, ran, "=D{0}+E{0}".format(self.startParticipantRow+i)))

     # Имена шапки "суммарно"
     ran = sheetTitle + "!A{0}".format(self.summaryRow)
     data.append(ce.insertValue(spId, ran, words[-1]))

     return data



 def prepareBody(self, spId, collectNum = 0, collectName = "Коллективка"):
     '''
     подготовка json запроса для заполнения таблицы лота информауией

     :param spId: айди листа в таблице
     :param collectNum: номер коллективки
     :param collectName: название коллективки (Коллективка/Индивидуалка)
     :return: возвращает json запрос
     '''

     body = {}
     body["valueInputOption"] = "USER_ENTERED"
     body["data"] = self.prepareValues(spId)

     return body
