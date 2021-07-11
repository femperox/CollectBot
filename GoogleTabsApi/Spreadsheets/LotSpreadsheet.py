import GoogleTabsApi.Cells_Editor as ce
from GoogleTabsApi.Styles.Borders import Borders as b

class Lots():

 spreadsheetsIds = {}

 def __init__(self, sheetList):
   self.spreadsheetsIds['Lera'] = (sheetList[0]['properties']['sheetId'], 0)
   self.spreadsheetsIds['Dasha_lot'] = (sheetList[3]['properties']['sheetId'], 3)
   self.spreadsheetsIds['Dasha_ind'] = (sheetList[4]['properties']['sheetId'], 4)
   self.spreadsheetsIds['Dasha_rf'] = (sheetList[5]['properties']['sheetId'], 5)
   self.spreadsheetsIds['Dasha_arc'] = (sheetList[6]['properties']['sheetId'], 6)
   self.spreadsheetsIds['Test'] = (sheetList[8]['properties']['sheetId'], 8)

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
    ''' подготовка json запроса для создания таблицы лота

     :param sheetList: Список свойств листов таблицы
     :param spId: айди листа в таблице
     :param participants: количество участников лота
     :return: возвращает json запрос
    '''

    request = []
    startLotRow = self.findFreeRaw(sheetList, spId)
    startParticipantRow = startLotRow + 14
    summaryRow = startParticipantRow + participants

    request.append(ce.mergeCells(spId, "A{0}:B{0}".format(startLotRow)))
    request.append(ce.mergeCells(spId, "D{0}:D{1}".format(startLotRow, startLotRow+13)))
    request.append(ce.mergeCells(spId, "E{0}:E{1}".format(startLotRow, startLotRow+13)))
    request.append(ce.mergeCells(spId, "F{0}:F{1}".format(startLotRow, startLotRow+13)))
    request.append(ce.mergeCells(spId, "G{0}:G{1}".format(startLotRow, startLotRow+13)))
    request.append(ce.mergeCells(spId, "A{0}:C{1}".format(startLotRow+1, startLotRow+13)))  # место для картинки
    request.append(ce.mergeCells(spId, "A{0}:C{0}".format(summaryRow))) # для "суммарно"


    for i in range(participants):
        request.append(ce.mergeCells(spId, "B{0}:C{0}".format(startParticipantRow+i)))

    request.append(ce.setCellBorder(spId, "A{0}:G{1}".format(startLotRow, summaryRow), bstyleList=b.plain_black))
    request.append(ce.setCellBorder(spId, "H{0}:I{1}".format(startLotRow, startLotRow+2), bstyleList=b.plain_black))
    request.append(ce.setCellBorder(spId, "H{0}:I{1}".format(startLotRow+3, summaryRow), only_outer= True, bstyleList=b.plain_black))

    return request

