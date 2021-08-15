from pprint import pprint
import GoogleTabsApi.GoogleTabs as gt
import VkApi.VkInterface as vki
#import VkApi.VkAccessToken as vkt

def createNamedRange(who, num:int, what = "Collect"):

    # тут сделать проверку по айди
    result = who

    # пока хз чё
    result += what

    result += str(num)

    return result

def createMessage(collect, lotWallUrl, dorazbivWallUrl = None, where = "Краснодар" ):

    dorazbiv = "" if dorazbivWallUrl == None else "Доразбив: {0}\n".format(dorazbivWallUrl)

    collectType, collectNum = table.sp.defineCollectType(collect)

    mes = collectType +" "+str(collectNum) +"\n"\
          "Лот: {0}\n".format(lotWallUrl) +\
          dorazbiv +\
          "\nСостояние: Выкупается \n" +\
          "TESTING" +\
          "\nПоедет в {0}".format(where) # сделать определение куда

    return mes


def strToList(string):
    return string.split(", ")

def checkItems(itemsList, itemsNumList):

    correctItemsList = itemsList.copy()

    for i in itemsList:
        try:
            itemsNumList.remove(int(i))
        except:
            correctItemsList.remove(i)
            print("it was referenced before")

    return correctItemsList

def checkParticipants(participantsList, items_num):

    items_num = [i+1 for i in range(items_num)]
    print(items_num)

    print("let's check items and participants!")
    correctList = []

    for i in range(len(participantsList)):

        inp = input("{0} :".format(participantsList[i][1]))

        if len(inp)>0 and inp!="-":
            listInp = checkItems(strToList(inp), items_num)
            correctList.append( (listInp, participantsList[i] ))

    if len(items_num) != 0:
        inp = input("There are {} items, which were not used! Add participants? y/n".format(len(items_num)))
        if inp == "y":
            inp = int(input("How many: "))


    pprint(correctList)
    pprint(items_num)

def createTableTopic(post_url, spId=0, topicName=0, items=0, img_url=0):

    tt=vk.get_active_comments_users_list(post_url)
    pprint(tt)
    print(len(tt[0]))
    checkParticipants(tt[0],21)

    #table.createTable(spId, items, image= img_url)

    #vk.post_comment()


    pass


if __name__ == '__main__':

    vk = vki.BoardBot()
    table = gt.GoogleTabs()

    createTableTopic("https://vk.com/wall-200887174_7673")


    #pprint(table.sp.spreadsheetsIds)

    #pprint(table.getParticipantsList(1401862322, "DCollect144"))




    # TESTING
    pList = []
    pList.append(([1, 2], "Name1"))
    pList.append(([3], "Name2"))

    request = \
        { "participants" : len(pList),
          "participantList": pList
        }

