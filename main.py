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
    :param dorazbivWallUrl:
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

    items_num = [i+1 for i in range(items_num)]
    print(items_num)

    print("let's check items and participants!")
    correctList = []

    for i in range(len(participantsList)):

        inp = input("{0} :".format(participantsList[i][1]))

        tryMakeCorrectItemList(inp, items_num, participantsList[i], correctList)

    if len(items_num) != 0:
        pprint(items_num)
        inp = input("There are {} items, which were not used! Add participants? y/n".format(len(items_num)))
        if inp == "y":
            inp = int(input("How many: "))

            for i in range(inp):
                name, id = input("Enter name and vk id of participant. if it's you id = 0:' ").split(" ")
                items = input("Items: ")
                if id == "0":
                    tryMakeCorrectItemList(items, items_num, name, correctList)
                else:
                    tryMakeCorrectItemList(items, items_num, (id, name), correctList)

    if len(items_num) != 0:
        pprint(items_num)
        for x in items_num:
            correctList.append(([x], " "))

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

    if len(participantsList)> 1:
        for i in range(len(participantsList) - 1):
            pl = list(set(participantsList[i][0] + participantsList[i + 1][0]))
    else:
        pl = participantsList[0][0]

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

    namedRange = createNamedRange("L", collectNum)

    table.createTable(spId, namedRange, participants= items, image = img_url)

    participantsList = makeDistinctList(post_url)
    participantsList = checkParticipants(participantsList, items)
    participantsList.sort()

    mes = createMessage(namedRange, transformToTopicFormat(participantsList), post_url, where= "Железнодорожный")


    topicUrl = vk.post_comment(topicName, mes, img_urls=[img_url])

    table.updateTable(namedRange, transformToTableFormat(participantsList), topicUrl)




if __name__ == '__main__':

    vk = vki.BoardBot()
    table = gt.GoogleTabs()

    pprint(table.sp.spreadsheetsIds)

    topicName = "Лоты и индивидуалки"

    wallPosts = ['https://vk.com/wall-200887174_8069', 'https://vk.com/wall-200887174_8098']

    createTableTopic(wallPosts,collectNum=159, topicName= topicName, spId = 0, items= 19, img_url= 'https://sun9-41.userapi.com/impg/YndPJ7b_fS4ow_mH6hczCi1CDm0ThuQ5nPQR6w/_IqQa9M2eEE.jpg?size=1200x900&quality=96&sign=cba1d5a273b4af02298b107a36418406&type=album')





