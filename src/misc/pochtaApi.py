from suds.client import Client
from pprint import pprint
import json
import sqlalchemy
from sqlalchemy import func
from sqlalchemy.orm import Session

def getTracking(barcode):
    '''
    Возвращает информационный справочник по отправлению

    :param barcode: трек-номер отправеления
    :return:
    '''

    tmp_dict = json.load(open('privates.json', encoding='utf-8'))
    login = tmp_dict['pochta_login']
    psw = tmp_dict['pochta_psw']

    message = \
        """<?xml version="1.0" encoding="UTF-8"?>
                        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:oper="http://russianpost.org/operationhistory" xmlns:data="http://russianpost.org/operationhistory/data" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
                        <soap:Header/>
                        <soap:Body>
                           <oper:getOperationHistory>
                              <data:OperationHistoryRequest>
                                 <data:Barcode>""" + barcode + """</data:Barcode>  
                                 <data:MessageType>0</data:MessageType>
                                 <data:Language>RUS</data:Language>
                              </data:OperationHistoryRequest>
                              <data:AuthorizationHeader soapenv:mustUnderstand="1">
                                 <data:login>""" + login + """</data:login>
                             <data:password>""" + psw + """</data:password>
                          </data:AuthorizationHeader>
                       </oper:getOperationHistory>
                    </soap:Body>
                 </soap:Envelope>"""

    url = 'https://tracking.russianpost.ru/rtm34?wsdl'
    client = Client(url, headers={'Content-Type': 'application/soap+xml; charset=UTF-8'},
                         location='https://tracking.russianpost.ru/rtm34/')

    result = client.service.getOperationHistory(__inject={'msg':message.encode()})

    current_stat = result[0][-1]

    parcel = {}
    parcel['barcode'] = barcode
    parcel['sndr'] = current_stat['UserParameters']['Sndr']
    parcel['rcpn'] = current_stat['UserParameters']['Rcpn']
    parcel['destinationIndex'] = current_stat['AddressParameters']['DestinationAddress']['Index']
    parcel['operationIndex'] = current_stat['AddressParameters']['OperationAddress']['Index']
    parcel['operationDate'] = current_stat['OperationParameters']['OperDate']
    parcel['operationType'] = current_stat['OperationParameters']['OperType']['Name']

    try:
        parcel['operationAttr'] = current_stat['OperationParameters']['OperAttr']['Name']
    except:
        parcel['operationAttr'] = 'none'

    try:
        parcel['mass'] = current_stat['ItemParameters']['Mass']
    except:
        parcel['mass'] = 0

    return parcel

def insertDB(barcode, vk_id):

    tmp_dict = json.load(open('privates.json', encoding='utf-8'))
    login = tmp_dict['bd_login']
    psw = tmp_dict['bd_psw']
    host = tmp_dict['bd_host']

    info = getTracking(barcode)
    info['rcpnVkId'] = vk_id

    engine = sqlalchemy.create_engine(f"postgresql+psycopg2://{login}:{psw}@{host}/Pochta")
    #engine.connect()
    session = Session(bind=engine)


    session.execute("Call ParcelInsertUpdate( '{0}', '{1}', '{2}', {3}, {4}, '{5}', '{6}', '{7}', {8}, '{9}', {10})".format
                  ( info['barcode'], info['sndr'], info['rcpn'],
                     info['destinationIndex'], info['operationIndex'],
                     info['operationDate'], info['operationType'], info['operationAttr'],
                     info['mass'], info['rcpnVkId'], False
                   ))
    session.commit()



