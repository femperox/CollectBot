from pprint import pprint
import GoogleTabsApi.GoogleTabs as gt
import VkApi.VkInterface as vki
#import VkApi.VkAccessToken as vkt
import re

def createNamedRange(who, num:int, what = "Collect"):
    '''
    Генерирует именованный диапозон. Нужно доработать

    :param who:
    :param num:
    :param what:
    :return:
    '''

    # тут сделать проверку по айди
    result = who

    # пока хз чё
    result += what

    result += str(num)

    return result

def createMessage(collect, participantList, lotWallUrl, dorazbivWallUrl = None, where = "Краснодар" ):
    '''
    Создаёт текст комента в обсуждении по заданным параметрам

    :param collect:
    :param participantList:
    :param lotWallUrl:
    :param dorazbivWallUrl:
    :param where:
    :return:
    '''

    dorazbiv = "" if dorazbivWallUrl == None else "Доразбив: {0}\n".format(dorazbivWallUrl)

    collectType, collectNum = table.sp.defineCollectType(collect)

    mes = collectType +" "+str(collectNum) +"\n"\
          "Лот: {0}\n".format(lotWallUrl) +\
          dorazbiv +\
          "\nСостояние: Выкупается \n\n" +\
          participantList +\
          "\nПоедет в {0}".format(where) # сделать определение куда

    return mes


def strToList(string):
    '''
    Переводит строку в список

    :param string:
    :return:
    '''
    return string.split(", ")

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

    items_num = [i+1 for i in range(items_num)]
    print(items_num)

    print("let's check items and participants!")
    correctList = []

    for i in range(len(participantsList)):

        inp = input("{0} :".format(participantsList[i][1]))

        tryMakeCorrectItemList(inp, items_num, participantsList[i], correctList)

    if len(items_num) != 0:
        inp = input("There are {} items, which were not used! Add participants? y/n".format(len(items_num)))
        if inp == "y":
            inp = int(input("How many: "))

            for i in range(inp):
                name, id = input("Enter name and vk id of participant:' ").split(" ")
                items = input("Items: ")

                tryMakeCorrectItemList(items, items_num, (name,id), correctList)

    return correctList

def transformToTableFormat(participantsList):
    '''
    Переводит список позиций и участников в табличный вид для обновления таблицы

    :param participantsList: Список позиций и участников
    :return: возвращает словарь
    '''

    pList = []

    for p in participantsList:
        hyperlink = '=HYPERLINK("{0}"; "{1}")'.format(p[1][0],p[1][1])
        pList.append((p[0],hyperlink))

    pList = \
        { "participants" : len(pList),
          "participantList": pList
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
        participant = "@{0}({1})".format(getIdFromUrl(p[1][0]), p[1][1])
        pList += "{0} - {1}\n".format(items, participant)

    return pList

def createTableTopic(post_url, spId=0, topicName=0, items=0, img_url="https://i.pinimg.com/originals/50/d8/03/50d803bda6ba43aaa776d0e243f03e7b.png"):
    '''
    Создаёт таблицу и комент в обсуждении по заданным параметрам

    :param post_url:
    :param spId:
    :param topicName:
    :param items:
    :param img_url:
    :return:
    '''

    namedRange = createNamedRange("D", 1)

    table.createTable(spId, namedRange, participants= items, image = img_url)

    participantsList = vk.get_active_comments_users_list(post_url)

    participantsList = checkParticipants(participantsList[0], items)

    table.updateTable(namedRange, transformToTableFormat(participantsList))

    mes = createMessage(namedRange, transformToTopicFormat(participantsList),post_url )
    vk.post_comment(topicName, mes, img_urls=[img_url])


if __name__ == '__main__':

    vk = vki.BoardBot()
    table = gt.GoogleTabs()

    createTableTopic("https://vk.com/wall-200887174_7949", topicName= "Лоты и индивидуалки", spId = 158683993, items= 5)


    pprint(table.sp.spreadsheetsIds)


