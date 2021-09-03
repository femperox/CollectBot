import GoogleTabsApi.Cells_Editor as ce
from GoogleTabsApi.Styles.Borders import Borders as b
from GoogleTabsApi.Styles.Colors import Colors as c
import re

class Lots():

 spreadsheetsIds = {}
 startLotRow = 0
 startParticipantRow = 0
 summaryRow = 0

 def __init__(self, sheetList):

   '''
   for i in range(len(sheetList)):
       self.spreadsheetsIds[sheetList[i]['properties']['title']] = (sheetList[i]['properties']['sheetId'], sheetList[i]['properties']['index'], sheetList[i]['properties']['title'])
   '''
   self.spreadsheetsIds[sheetList[0]['properties']['title']] = (sheetList[0]['properties']['sheetId'], sheetList[0]['properties']['index'])
   self.spreadsheetsIds[sheetList[3]['properties']['title']] = (sheetList[3]['properties']['sheetId'], sheetList[3]['properties']['index'])
   self.spreadsheetsIds[sheetList[4]['properties']['title']] = (sheetList[4]['properties']['sheetId'], sheetList[4]['properties']['index'])
   self.spreadsheetsIds[sheetList[5]['properties']['title']] = (sheetList[5]['properties']['sheetId'], sheetList[5]['properties']['index'])
   self.spreadsheetsIds[sheetList[6]['properties']['title']] = (sheetList[6]['properties']['sheetId'], sheetList[6]['properties']['index'])
   self.spreadsheetsIds[sheetList[8]['properties']['title']] = (sheetList[8]['properties']['sheetId'], sheetList[8]['properties']['index'])
   self.spreadsheetsIds[sheetList[9]['properties']['title']] = (sheetList[9]['properties']['sheetId'], sheetList[9]['properties']['index'])

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

 def findName(self, spId):
     '''
     Поиск имени листа по его айди

     :param spId: айди листа в таблице
     :return: возвращает строчку-имя
     '''

     spItems = list(self.spreadsheetsIds.items())

     for i in range(len(spItems)):
         if spItems[i][1][0] == spId:
             return spItems[i][0]


 def prepareLot(self, sheetList, spId, participants = 1, rangeName = ""):
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

    request.append(ce.addNamedRange(spId, "A{0}:I{1}".format(self.startLotRow, self.summaryRow), rangeName))

    return request

 def defineCollectType(self, collect):
     '''
     Определяет тип коллективки. Т.е. её номер и (коллективка/индивидуалка)

     :param collect: название именованного диапозона
     :return: возвращает тип коллекта и его номер
     '''

     try:
        collectType, collectNum = re.split(r"\d", collect, 1)
        collectNum = collect[len(collectType)] + collectNum
     except:
         collectType = collect
         collectNum = 0
     collectType = "Коллективка" if collectType.find("Collect")>=0 else "Индивидуалка"

     return collectType, collectNum


 def prepareValues(self, spId, image, collect = ""):
     '''
     подготовка блока data в json-запросе для заполнения таблицы значениями

     :param spId: айди листа в таблице
     :param collect: название именованного диапозона
     :return: возвращает часть json запроса
     '''

     collectType, collectNum = self.defineCollectType(collect)

     data = []

     participants = self.summaryRow - self.startParticipantRow


     sheetTitle = self.findName(spId)

     ran = sheetTitle +"!A{0}:B{0}".format(self.startLotRow)
     data.append(ce.insertValue(spId, ran, "{1} №{0}   Трек:".format(collectNum, collectType)))

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

     # Изображение лота
     ran = sheetTitle + "!A{0}".format(self.startLotRow+1)
     image = '=IMAGE("{0}")'.format(image)
     data.append(ce.insertValue(spId, ran, image))

     # Для расчётов
     form = "!I{0}"
     ran = sheetTitle + form.format(self.startLotRow+3)
     data.append(ce.insertValue(spId, ran, 227))

     ran = sheetTitle + form.format(self.startLotRow+4)
     formula = "=I{0}/300".format(self.startLotRow+3)
     data.append(ce.insertValue(spId, ran, formula))

     for i in range(2):
         row = self.startLotRow+6+i
         ran = sheetTitle + form.format(row)
         formula = "=CEILING(H{0}*I{1})".format(row, self.startLotRow+4)
         data.append(ce.insertValue(spId, ran, formula))

         ran = sheetTitle + "!H{0}".format(row)
         data.append(ce.insertValue(spId, ran, 0))

     for i in range(ord('H'), ord('I')+1):
         row = self.startLotRow + 8
         ran = sheetTitle + "!{0}{1}".format(chr(i), row)
         formula = "= {0}{1} + {0}{2}".format(chr(i), row - 2, row -1)
         data.append(ce.insertValue(spId,ran,formula))

     return data



 def prepareBody(self, spId, image, collect = ""):
     '''
     подготовка json запроса для заполнения таблицы лота информауией

     :param spId: айди листа в таблице
     :param collect: название именованного диапозона
     :return: возвращает json запрос
     '''

     body = {}
     body["valueInputOption"] = "USER_ENTERED"
     body["data"] = self.prepareValues(spId, image, collect)

     return body


 def changeList(self, sheetList, newSpId, collectId, collectNamedRange):
     '''
     Перемещение таблицы с одного листа на другой

     :param sheetList: Список свойств листов таблицы
     :param newSpId: айди листа в таблице, куда нужно перенести таблицу
     :param collectId: имя именованного диапозона, совпадающего с именем коллективки
     :param collectNamedRange: именованный диапозон в формате "В1:С45" - пример
     :return: возвращает json запрос
     '''

     newRange = "A{0}".format(self.findFreeRaw(sheetList, newSpId))

     oldSheetTitle, oldRange = collectNamedRange.split("!")

     oldSpId = self.spreadsheetsIds[oldSheetTitle[1:len(oldSheetTitle)-1]][0]
                #self.spreadsheetsIds[oldSheetTitle][0]

     request = []

     request.append(ce.CutPasteRange(oldSpId, oldRange, newRange, newSpId))
     request.append(ce.deleteNamedRange(collectId))

     convertedRange = oldRange.split(":")

     # Удаляем со старого места таблицу и пустую строку под ней
     oldRangeWithBlankRow = convertedRange[0] +":" + convertedRange[1][0] + str( int(convertedRange[1][1:])+1)
     request.append(ce.deleteRange(oldSpId, oldRangeWithBlankRow))

     # Сопостовление индексов для нового места
     convertedRange = int(convertedRange[1][1:]) - int(convertedRange[0][1:]) + int(newRange[1:])
     newRange += ':I{0}'.format(convertedRange)

     request.append(ce.addNamedRange(newSpId, newRange, collectId))

     return request

 def updateBaseOfLot(self, collectNamedRange, participants):
     '''
     Обновление таблицы в соотвествии с количеством участников коллективки

     :param collectNamedRange: именованный диапозон в формате "В1:С45" - пример
     :param participants: количество участников
     :return: возвращает json запрос
     '''

     request = []

     sheetTitle, range = collectNamedRange.split("!")
     spId = self.spreadsheetsIds[sheetTitle[1:len(sheetTitle)-1]][0]

     range = range.split(":")

     self.startParticipantRow = int(range[0][1:]) + 14
     rowsAmount = int(range[1][1:]) - self.startParticipantRow

     if participants <= rowsAmount:
        rangeToDelete = "A{0}:I{1}".format( self.startParticipantRow + participants, int(range[1][1:])-1 )
        request.append(ce.deleteRange(spId, rangeToDelete))

     return request

 def listToString(self, list):
    '''
    Переводит список в строчку в формате "x, y, z"

    :param list: список
    :return: возвращает строку
    '''

    itemString = ""

    for i in range(len(list)):
        itemString += str(list[i])+", "

    return itemString[:-2]


 def updateBaseValues(self, collectNamedRange, participantsInfo, topicUrl):
     '''
     Обновляет значения ячеек: позиции, участники

     :param collectNamedRange: именованный диапозон в формате "В1:С45" - пример
     :param participantsInfo: список с инфой об участнике и его позициях
     :return: возвращает json запрос
     '''

     body = {}
     body["valueInputOption"] = "USER_ENTERED"

     data = []
     sheetTitle, rangeParticipants = collectNamedRange.split("!")
     spId = self.spreadsheetsIds[sheetTitle[1:len(sheetTitle)-1]][0]


     for i in range(len(participantsInfo)):
         ran = sheetTitle + "!A{0}".format(self.startParticipantRow+i)
         data.append(ce.insertValue(spId, ran, self.listToString(participantsInfo[i][0]) ) )
         ran = ran.replace('A', 'B', 1)
         data.append(ce.insertValue(spId, ran, participantsInfo[i][1] ) )

     topicUrl = '=HYPERLINK("{0}"; "тык")'.format(topicUrl)
     ran = sheetTitle + "!I{0}".format(self.startLotRow+2)
     data.append(ce.insertValue(spId, ran, topicUrl))


     body["data"] = data
     return body



