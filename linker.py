from pprint import pprint
import GoogleTabsApi.GoogleTabs as gt
import VkApi.VkInterface as vki
import re

def createNamedRange(spId, who, num:int):
    '''
    Генерирует именованный диапозон. Нужно доработать

    :param who:
    :param num:
    :param what:
    :return:
    '''

    # тут сделать проверку по айди
    result = who

    if spId == table.sp.spreadsheetsIds['Дашины лоты'][0] or spId == table.sp.spreadsheetsIds['Лерины лоты'][0]:
    # пока хз чё
        result += "Collect"
    else: result += 'Ind'

    result += str(num)

    return result

def createDorazbivStrings(lotWallUrl):
    '''
    Создаёт строки со ссылками на доразбивы

    :param lotWallUrl:
    :return:
    '''

    dorazbivStrings = ""
    for i in range(1, len(lotWallUrl)):
        dorazbivStrings += "Доразбив{0}: {1}\n".format("" if i==1 else i, lotWallUrl[i])

    return dorazbivStrings


def createMessage(collect, participantList, lotWallUrl, where = "Краснодар" ):
    '''
    Создаёт текст комента в обсуждении по заданным параметрам

    :param collect:
    :param participantList:
    :param lotWallUrl:
    :param where:
    :return:
    '''

    collectType, collectNum = table.sp.defineCollectType(collect)

    mes = collectType +" "+str(collectNum) +"\n"\
          "Лот: {0}\n".format(lotWallUrl[0]) +\
          createDorazbivStrings(lotWallUrl) +\
          "\nСостояние: Выкупается \n\n" +\
          participantList +\
          "\nПоедет в {0}".format(where) # сделать определение куда

    return mes


def strToList(string):
    '''
    Переводит строку в отсортированный список

    :param string:
    :return:
    '''

    list = string.split(", ")
    list = [int(x) for x in list]
    list.sort()

    return list

def checkItems(itemsList, itemsNumList):
    '''
    Проверка на повтор айтемов

    :param itemsList:
    :param itemsNumList:
    :return:
    '''

    correctItemsList = itemsList.copy()

    for i in itemsList:
        try:
            itemsNumList.remove(int(i))
        except:
            correctItemsList.remove(i)
            print("it was referenced before")

    return correctItemsList

def tryMakeCorrectItemList(inp, items_num, participant, correctList):
    '''
    Добавление участника и его айтемов в общий список

    :param inp:
    :param items_num:
    :param participant:
    :param correctList:
    :return:
    '''

    if len(inp) > 0 and inp != "-":
        listInp = checkItems(strToList(inp), items_num)
        correctList.append((listInp, participant))


def checkParticipants(participantsList, items_num):
    '''
    Проверка айтемов и участников

    :param participantsList:
    :param items_num:
    :return:
    '''
    items_num = [i + 1 for i in range(items_num)]
    print(items_num)

    print("let's check items and participants!")
    correctList = []

    flag = 0

    while len(items_num)!=0:

        if flag == 0:
            for i in range(len(participantsList)):
                inp = input("{0} :".format(participantsList[i][1]))
                tryMakeCorrectItemList(inp, items_num, participantsList[i], correctList)
                if len(items_num) == 0: break
        elif flag == 1:
            if len(items_num) != 0:
                pprint(items_num)
                inp = input("There are {} items, which were not used! Add participants? y/n".format(len(items_num)))
                if inp == "y":
                    inp = int(input("How many: "))

                    for i in range(inp):
                        id = input("Enter name and vk id of participant. if it's you id = 0:' ")
                        name = re.split(r'https://vk.com/id\d+', id)[0]

                        if name!=id:
                            id = id[len(name):]
                        else:
                            name, id = name.split(" ")

                        items = input("Items: ")
                        if id == "0":
                            tryMakeCorrectItemList(items, items_num, name, correctList)
                        else:
                            tryMakeCorrectItemList(items, items_num, (id, name), correctList)
        else:
            pprint(items_num)
            for x in items_num:
                correctList.append(([x], " "))
            items_num = []
        flag += 1

    return correctList


def transformToTableFormat(participantsList):
    '''
    Переводит список позиций и участников в табличный вид для обновления таблицы

    :param participantsList: Список позиций и участников
    :return: возвращает словарь
    '''

    pList = []

    for p in participantsList:
        if isinstance(p[1], str):
            hyperlink = p[1]
        else:
            hyperlink = '=HYPERLINK("{0}"; "{1}")'.format(p[1][0],p[1][1])
        pList.append((p[0],hyperlink))

    pList = \
        { "participants" : len(pList),
          "participantList": pList,
        }

    return pList

def getIdFromUrl(url):
    '''
    Получает номер id пользователя vk из ссылки

    :param url: ссылка на пользователя в формате https://vk.com/id{числа}
    :return: возвращает часть строки, начиная с id
    '''

    return re.findall(r"id\d+", url)[0]

def transformToTopicFormat(participantsList):
    '''
    Переводит список позиций и участников в строковый вид для поста в обсуждении

    :param participantsList: Список позиций и участников
    :return: возвращает строчку
    '''

    pList = ""

    for p in participantsList:
        items = table.sp.listToString(p[0])
        if isinstance(p[1], str):
            participant = p[1]
        else:
            participant = "@{0}({1})".format(getIdFromUrl(p[1][0]), p[1][1])
        pList += "{0} - {1}\n".format(items, participant)

    return pList

def makeDistinctList(post_url):
    '''
    Создаёт список уникальных пользователей с нескольких/одной записи

    :param post_url: список адресов записей на стене сообщества
    :return:
    '''

    participantsList = []
    for url in post_url:
        participantsList.append(vk.get_active_comments_users_list(url))

    pl = []
    for i in range(len(participantsList)):
            pl = list(set(pl + participantsList[i][0]))

    return pl


def createTableTopic(post_url, collectNum = 0, spId=0, topicName=0, items=0, img_url="https://i.pinimg.com/originals/50/d8/03/50d803bda6ba43aaa776d0e243f03e7b.png"):
    '''
    Создаёт таблицу и комент в обсуждении по заданным параметрам

    :param post_url: список адресов записей на стене сообщества
    :param spId:
    :param topicName:
    :param items:
    :param img_url:
    :return:
    '''

    namedRange = createNamedRange(spId, "D", collectNum)

    participantsList = makeDistinctList(post_url)
    participantsList = checkParticipants(participantsList, items)
    participantsList.sort()

    mes = createMessage(namedRange, transformToTopicFormat(participantsList), post_url)

    topicInfo = vk.post_comment(topicName, mes, img_urls=[img_url])

    table.createTable(spId, namedRange, participants= items, image = topicInfo[1][0])
    table.updateTable(namedRange, transformToTableFormat(participantsList), topicInfo[0])

# Доработать!!!!
def ShipmentToRussiaEvent(toSpId, lotList):

    for i in range(len(lotList)):
        lotList[i] = 'DCollect'+str(lotList[i])
        table.moveTable(toSpId, lotList[i])


if __name__ == '__main__':

    vk = vki.BoardBot()
    table = gt.GoogleTabs()

    pprint(table.sp.spreadsheetsIds)

    topicName = "Лоты и индивидуалки"

    wallPosts = ['https://vk.com/wall-200887174_8729', 'https://vk.com/wall-200887174_8791']

    dashaLot = 1401862322
    dashaLotRF = 333654542
    dashaInd = 2011848664
    leraLot = 0
    test = 158683993

    img = 'https://sun9-31.userapi.com/impg/1cPIhwhYtstWnJF6ssg0cDckXkPluqEUSoSBBw/jj1u33aCafM.jpg?size=1200x1010&quality=96&sign=31d90b152f25ded44ab4728ed4b2ae1a&type=album'
    createTableTopic(wallPosts, collectNum=178, topicName= topicName, spId = dashaLot,  items= 18, img_url= img)



    #ShipmentToRussiaEvent(dashaLotRF, lotList)