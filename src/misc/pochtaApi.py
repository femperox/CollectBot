from suds.client import Client
from pprint import pprint
import json

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
    parcel['operationAttr'] = current_stat['OperationParameters']['OperAttr']['Name']
    parcel['mass'] = current_stat['ItemParameters']['Mass']

    return parcel


barcode = '80111471834158' #баркод
getTracking(barcode)