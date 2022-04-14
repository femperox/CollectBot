from bs4 import BeautifulSoup
import requests
from pprint import pprint
import re

def makeSoup(url):
    headers = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
              }

    page = requests.get(url, headers)

    soup = BeautifulSoup(page.text, "html.parser")

    return soup

def parcePage(url):
    '''
    Парсит страницу по заданному url
    :param url: url-адрес
    :return: список жанров со страницы
    '''

    soup = makeSoup(url)


    item = {}
    item['priceYen'] = soup.find('span', id = 'lblPriceY').text[1:].replace(',','')
    item['percentTax'] = soup.find('span', id = 'lblTax').text.replace(',','')
    item['priceShipmt'] = soup.find('span', id = 'lblChargeForShipping').text
    item['yahooPage'] = soup.find('a', id = 'productPage').get('href')

    try:
        item['percentTax'] = re.findall('¥(\d+)', item['percentTax'])[0]
    except:
        item['percentTax'] = 0

    return item

def findShipmentPrice(url):
    '''придумать как решить, не даёт пропарсить цену доставки'''

    soup = makeSoup(url)

    price = soup.find_all('ul', class_ = 'BidModal__postageArea js-postexpand-modalBody')

    return price
