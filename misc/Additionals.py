def concatList(list1, list2):
    '''
    связывает два массива типа [ [...], ... [...]] поэлементно

    :param list1:
    :param list2:
    :return: список
    '''

    resultList = []
    for i in range(len(list1)):
        resultList.append([list1[i], list2[i]])

    return resultList

