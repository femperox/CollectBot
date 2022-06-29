import json

from bs4 import BeautifulSoup
from seleniumwire import webdriver
import requests
from pprint import pprint
import re
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
import xmltodict
from pathlib import Path
import os

def makeSoup(url):
    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36'
              }

    page = requests.get(url, headers, timeout=20)

    soup = BeautifulSoup(page.text, 'lxml')
    return soup

def getHeader():

    headers = {
        'User-Agent': ': Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 OPR/86.0.4363.64',
        'Content-Type': 'application/json, text/plain, */*',
        'x-platform': 'web',
    }

    return headers


def parseMercariPage(url):

    session = requests.session()
    curl = f'https://api.mercari.jp/items/get?id={getItemID(url)}'

    ok = webdriver.Chrome(ChromeDriverManager().install())
    ok.get(url)
    sleep(15)

    for request in ok.requests:
        if request.url.find('get?id=')>0:
            dpop = request.headers['dpop']

    headers = getHeader()

    headers['dpop'] = dpop
    page = session.get(curl, headers=headers)
    js = page.json()

    pprint(js)

    item = {}
    item['priceYen'] = js['data']['price']
    item['percentTax'] = 0
    item['priceShipmt'] = 0
    item['page'] = url
    item['mainPhoto'] = js['data']['photos'][0]
    item['siteName'] = 'mercari'

    return item

def parsePayPay(url):

    curl = f'https://paypayfleamarket.yahoo.co.jp/api/item/v2/items/{getItemID(url)}'

    headers = getHeader()
    page = requests.get(curl, headers=headers)
    js = page.json()

    item = {}
    item['priceYen'] = js['price']
    item['percentTax'] = 0
    item['priceShipmt'] = 0
    item['page'] = url
    item['mainPhoto'] = js['images'][0]['url']
    item['siteName'] = 'payPayFleamarket'

    return item

def parseYahooAuctions(url):

    path = os.getcwd()+ '/src/misc/privates.json'

    print(path)
    tmp_dict = json.load(open(path, encoding='utf-8'))
    app_id = tmp_dict['yahoo_jp_app_id']

    curl = f'https://auctions.yahooapis.jp/AuctionWebService/V2/auctionItem?appid={app_id}&auctionID={getItemID(url)}#'

    headers = getHeader()
    page = requests.get(curl, headers=headers)
    xml = xmltodict.parse(page.content)

    item = {}
    item['priceYen'] = xml['ResultSet']['Result']['Price']
    item['priceYen'] = item['priceYen'][:item['priceYen'].find('.')]
    pprint(item['priceYen'])
    item['percentTax'] = float(item['priceYen']) * float(xml['ResultSet']['Result']['TaxRate'])/100
    item['priceShipmt'] = 0 # потом додумать
    item['page'] = url
    item['mainPhoto'] = xml['ResultSet']['Result']['Img']['Image1']['#text']
    item['siteName'] = 'yahooAuctions'

    return item

def parseAmiAmiEng(url):

    id = getItemID(url)
    id = id[id.find('=')+1:].replace('&page=top','')
    print(id)

    curl = f'https://api.amiami.com/api/v1.0/item?gcode={id}'#&lang=jp'

    headers = getHeader()

    headers['x-user-key'] = 'amiami_dev'
    page = requests.get(curl, headers=headers)
    js = page.json()

    item = {}
    item['priceYen'] = js['item']['price']
    item['percentTax'] = 0
    item['priceShipmt'] = 0
    item['page'] = url
    item['mainPhoto'] = 'https://img.amiami.com'+js['item']['main_image_url']
    item['siteName'] = 'AmiAmiEng'
    item['name'] = js['item']['gname']

    pprint(item)

    pass

def parseAmiAmiJp(url):

    curl = 'https://jp-tags.mediaforge.com/js/4740/?prodID=FIGURE-140658'

    headers = getHeader()

    page = requests.get(curl, headers=headers)
    pprint(page.content)

    pass

def parseMandarake(url):

    ok = webdriver.Chrome(ChromeDriverManager().install())

    ok.implicitly_wait(10)
    ok.get(url)
    #sleep(10)

    for request in ok.requests:
        if request.url.find('getInfo') > 0:
            info = request.response.body

    pprint(info)
    pos_tax = str(info).find('"price_with_tax":')
    pos_price = str(info).find('"price":')
    pos_segment = str(info).find(',"segment')


    item = {}
    item['priceYen'] = str(info)[pos_price+len('"price":'):pos_segment]
    item['percentTax'] = int(str(info)[pos_tax+len('"price_with_tax":'):-2]) - int(item['priceYen'])
    item['priceShipmt'] = 0
    item['page'] = url
    #item['mainPhoto'] = 'https://img.amiami.com'+js['item']['main_image_url']
    item['siteName'] = 'Mandarake'
    #item['name'] = js['item']['gname']

    return item





def getSiteName(url):
    '''
    Возвращает название сайта (его домен)

    :param url: ссылка на товар
    :return:
    '''

    name = re.findall('//[a-zA-Z0-9_.]+/', url)[0][2:-1]
    name = name.replace('jp','').replace('com','').replace('www', '').replace('co', '').replace('order.', '').replace('.','')
    return name

def getItemID(url):

    id = url.split('/')[-1]
    return id

def parseSite(url):

    site = getSiteName(url)
    print(site)
    item = {}
    if site == 'zenmarket':
        pass
    elif site == 'mercari':
        item = parseMercariPage(url)
    elif site == 'paypayfleamarketyahoo':
        item = parsePayPay(url)
    elif site == 'pageauctionsyahoo':
        item = parseYahooAuctions(url)
    elif site == 'amiami':
        if url.find('/eng/')>0:
            item = parseAmiAmiEng(url)
        else:
            item = parseAmiAmiJp(url)
    elif site == 'mandarake':
        item = parseMandarake(url)


    return item



#site = 'https://jp.mercari.com/item/m80929854346'
#site = 'https://jp.mercari.com/item/m80929854346'
#site = 'https://paypayfleamarket.yahoo.co.jp/item/z127729404'
#site = 'https://www.amiami.com/eng/'
#site = 'https://page.auctions.yahoo.co.jp/jp/auction/h1052739834'
#site = 'https://page.auctions.yahoo.co.jp/jp/auction/x1053349147'
#site = 'https://zenmarket.jp/ru/auction.aspx?itemCode=s1033560471'
site = 'https://order.mandarake.co.jp/order/detailPage/item?itemCode=1183713270&ref=list&keyword=Bratz&lang=en'
#site = 'https://www.amiami.jp/top/detail/detail?gcode=GOODS-04242880&page=top'
#pprint(parseSite(site))
