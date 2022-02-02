from pprint import pprint
import GoogleTabsApi.GoogleTabs as gt
import VkApi.VkInterface as vki
import misc.ParseZen as zen
import re

from datetime import datetime

def createNamedRange(spId, who, find):
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
        find['key_word'] = 'Коллективка'
    else:
        result += 'Ind'
        find['key_word'] = 'Индивидуалка'

    num = int(vk.get_last_lot(find)) + 1
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

    mes = collectType +" "+str(collectNum) +"\n"
    if lotWallUrl[0] != '':
        mes += "Лот: {0}\n".format(lotWallUrl[0]) +\
                createDorazbivStrings(lotWallUrl)
    mes += "\nСостояние: Выкупается \n\n" +\
            participantList +\
            "\nПоедет в {0}".format(where)

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

    print('\n====================================\n')
    print("let's check items and participants!")
    correctList = []

    flag = 0

    while len(items_num)!=0:

        if flag == 0:
            for i in range(len(participantsList)):
                inp = input("{0} : ".format(participantsList[i][1]))
                tryMakeCorrectItemList(inp, items_num, participantsList[i], correctList)
                if len(items_num) == 0: break
        elif flag == 1:
            if len(items_num) != 0:

                print('\n===== Remains')
                pprint(items_num)
                print("Amount of items: ", len(items_num) )
                inp = input("There are {} items, which were not used! Add participants? y/n: ".format(len(items_num)))
                if inp == "y":
                    inp = int(input("How many: "))

                    for i in range(inp):
                        id = input("Enter vk url. if it's you, enter 'Мне': ' ")

                        try:
                            name, id = vk.get_num_id(id)
                        except:
                            name = id
                            id = '0'

                        items = input("Items: ")
                        if id == "0":
                            tryMakeCorrectItemList(items, items_num, name, correctList)
                        else:
                            tryMakeCorrectItemList(items, items_num, (id, name), correctList)
        else:
            print('\n===== Free')
            pprint(items_num)
            print("Amount of items: ", len(items_num))
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

        if isinstance(p[0], list):
            items = table.sp.listToString(p[0])
        else:
            items = p[0]

        try:
            participant = "@{0}({1})".format(getIdFromUrl(p[1][0]), p[1][1])
        except:
            participant = p[1]
        pList += "{0} - {1}\n".format(items, participant)

    return pList

def tableToTopic(participantsList):
    '''
    Из формата для таблиц переводит в формат для обсуждения

    :param participantsList: Список позиций и участников
    :return: возвращает строчку
    '''

    pList = ""

    for p in participantsList:

        p_url = re.findall('"(.+)";', p[1])

        try:
            p_name =  re.findall('; "(.+)"\)', p[1])[0]
            p[1] = [p_url[0], p_name]
        except:
            pass

    return transformToTopicFormat(participantsList)



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


def createTableTopic(post_url, zen_url = '', spId=0, topicName=0, items=0, img_url="https://i.pinimg.com/originals/50/d8/03/50d803bda6ba43aaa776d0e243f03e7b.png"):
    '''
    Создаёт таблицу и комент в обсуждении по заданным параметрам

    :param post_url: список адресов записей на стене сообщества
    :param spId:
    :param topicName:
    :param items:
    :param img_url:
    :return:
    '''

    if spId == table.sp.spreadsheetsIds['Лерины лоты'][0]:
        letter = 'L'
        where = 'Железнодорожный'
    else:
        letter = 'D'
        where = 'Краснодар'

    find = {'topic_name': topicName, 'collect_type': 'Индивидуалка'}

    namedRange = createNamedRange(spId, letter, find)

    participantsList = makeDistinctList(post_url) if post_url[0] != '' else []
    participantsList = checkParticipants(participantsList, items)
    participantsList.sort()

    mes = createMessage(namedRange, transformToTopicFormat(participantsList), post_url, where = where)

    topicInfo = vk.post_comment(topicName, mes, img_urls=[img_url])

    item = {}
    if zen_url != '':
        item = zen.parcePage(zen_url)

    table.createTable(spId, namedRange, participants= items, image = topicInfo[1][0], item = item)
    table.updateTable(namedRange, transformToTableFormat(participantsList), topicInfo[0])

def ShipmentToRussiaEvent(toSpId, collectList, indList):
    '''
    Активирует переброс лота с одного листа на другой
    :param toSpId:
    :param collectList: список номеров коллективок
    :param indList: список номеров индивидуалок
    :return:
    '''

    lotList = {'DCollect': [x for x in collectList], 'DInd': [x for x in indList]}

    for key in lotList.keys():
        for i in range(len(lotList[key])):
            if lotList[key][i] != '':
                table.moveTable(toSpId, key + lotList[key][i])

def changePositions(userList, topic_name = "Лоты и индивидуалки"):

    for yst in userList:

        try:
            number = int(yst[0])
            lot = "Collect{0}".format(number)
            type = "Коллективка"
        except:
            number = int(yst[0][1:])
            lot = "Ind{0}".format(number)
            type = "Индивидуалка"

        id = vk.get_num_id(yst[1][1])
        yst[1][1] = [id[1], id[0]]

        newParticipants = transformToTableFormat([yst[1]])
        try:
            actualParticipants = table.changePositions('D'+lot, newParticipants["participantList"])
        except:
            actualParticipants = table.changePositions('L'+lot, newParticipants["participantList"])

        actualParticipants = tableToTopic(actualParticipants)

        what_to_find = {
            "topic_name": topic_name,
            "type": type,
            "number": number
        }

        vk.edit_comment(actualParticipants, what_to_find)





def console():
    choise = 0

    while choise != 3:

      choise = int(input('\nВведите номер:\n1. Сделать лот\t2. Отправки в РФ\n3. Выход\t4. Замена ссылок на теги '
                         '\n5. Забанить\t6. Уступки\nВыбор: '))

      if choise == 1:

        topicName = "Лоты и индивидуалки"

        lists = [ table.sp.spreadsheetsIds['Лерины лоты'][0],
                  table.sp.spreadsheetsIds['Дашины лоты'][0],
                  table.sp.spreadsheetsIds['Дашины индивидуалки '][0],
                  table.sp.spreadsheetsIds['ТестЛист'][0]
                ]

        print('\nВыберите лист из таблицы:\n'
              '1. Лерины лоты\t2. Дашины лоты\n'
              '3. Дашины индивидуалки\t4. Тестовый лист'
              )
        choise1 = int(input('Выбор: '))

        spId = lists[choise1-1]

        zen_url = input('\nEnter the Zen url (might be empty): ')

        wallPosts = input('\nEnter the vk posts. If more than 1 - use space. (might be empty): ')
        wallPosts = wallPosts.split(' ')

        img = input('\nEnter the image url (might be empty): ')

        items = int(input('\nHow many items are there? '))

        if len(img) == 0:
            createTableTopic(wallPosts, zen_url, spId = spId,
                         topicName = topicName, items = items)
        else:
            createTableTopic(wallPosts, zen_url, spId=spId,
                             topicName=topicName, items=items, img_url=img)
      elif choise == 2:

        lists = [table.sp.spreadsheetsIds['Дашины лоты (Едет в РФ)'][0],
                 table.sp.spreadsheetsIds['Дашины лоты (Архив)'][0],
                 table.sp.spreadsheetsIds['ТестЛист'][0]
                ]

        print('\nВыберите лист из таблицы:\n'
              '1. Дашины лоты РФ\t2. Дашины лоты Архив\n'
              '3. Тестовый лист'
              )
        choise1 = int(input('Выбор: '))

        spId = lists[choise1 - 1]

        collectList = input("Enter collect's num using comma(, ) (might be empty): ")
        collectList = collectList.split(', ')

        indList = input("Enter ind's num using comma(, ) (might be empty): ")
        indList = indList.split(', ')

        ShipmentToRussiaEvent(spId, collectList, indList)

      elif choise == 4:
          topics = [ 'Лоты и индивидуалки',
                     'Гашапоны',
                     'AmiAmi',
                     'Коллект посылка до админа из Краснодара',
                     'Коллект посылка до админа из Москвы'
          ]

          print('\nВыберите обсуждение:\n'
                '1. {0}\t2. {1}\t3. {2}\n'
                '4. {3}\t5. {4}'.format(topics[0], topics[1], topics[2], topics[3], topics[4])
                )

          choise1 = int(input('Выбор: '))
          vk.replace_url(topics[choise1-1])

      elif choise == 5:

          user_list = []
          print('\nTo stop enter any symbol\n')

          i = 0

          while True:
            i += 1
            url = input('user{0} URL: '.format(i))
            if url.find('https://vk.com') < 0: break

            commentary = input('user{0} commentary: '.format(i))

            user_list.append({'id': url, 'comment': commentary })

          vk.ban_users(user_list)

      elif choise == 6:

          user_list = []
          print('\nTo stop enter any symbol\n')
          print('Если индивидуалка, то прицепить любой символ перед номером. Пример: и56')
          print('Запись в формате: 213 - 1, 2, 4\n')

          i = 0

          while True:
              i += 1
              url = input('user{0} URL: '.format(i))
              if url.find('https://vk.com') < 0: break

              lot, items = input('лот - уступка : '.format(i)).split(' - ')
              #items = items.split(', ')

              user_list.append([lot, [items, url]])

          changePositions(user_list)



# ДОДЕЛАТЬ
def paymentMessage():

    mes = 'это тестовое сообщение я просто тещу авторассылку'

    userList = ['https://vk.com/rimebright', 'https://vk.com/iwi11forgetmydreams']

    vk.payment_messege(mes, userList)

    print()

if __name__ == '__main__':

    table = gt.GoogleTabs()
    vk = vki.BoardBot()

    console()

    #date = datetime(2021,12,1).date()
    #vk.delete_photos("Ваши хотелки", date)


