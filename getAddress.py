
# http://g7s.truck.huoyunren.com/inside.php?t=json&m=map&f=getaddress
import logging
import requests
import io
import json
import os
import time
import datetime
import urllib
import hashlib
import pdb


from pymongo import MongoClient

from requests.auth import HTTPBasicAuth
# logging.basicConfig(level=logging.WARNING)
truckHistFile = '/test/truckHistData'
checkPointFile = '_checkPoint'

auth = HTTPBasicAuth('jhn_admin', 'jhnBJ74110')
tokenFile = io.open('token.txt', 'r', encoding='utf-8')
_TOKEN = tokenFile.readline()
logging.info('read token is ' + _TOKEN)
cookies = dict(_TOKEN=_TOKEN)
addressURL = 'http://g7s.truck.huoyunren.com/inside.php?t=json&m=map&f=getaddress'
geoAddressURL = 'http://api.map.baidu.com/geocoder/v2/'
# ak=E4805d16520de693a3fe707cdc962045&callback=renderReverse&location=39.983424,116.322987&output=json&pois=1
baiduAK = 'ki9OPCwL0o967ZHPgviMnDMCP3RwXIWZ'
baiduSK = '6a5Kg8e2z47ETsQHrsRU8GdfDZ6QKvoM'
params = dict()

logging.basicConfig(filename='log.log', level=logging.DEBUG)
logger = logging.getLogger()


def getToken():
    tokenFile = io.open('token.txt', 'r', encoding='utf-8')
    _TOKEN = tokenFile.readline()
    logging.info('read token is ' + _TOKEN)
    cookies = dict(_TOKEN=_TOKEN)
    return cookies


def getAddress(latitude, longtitude):
    cookies = getToken()
    formData = dict()
    formData['latlng'] = latitude + '&' + longtitude

    r = session.get(addressURL, data=formData, cookies=cookies, auth=auth)


def insertDB(db, jsonData):
    db.addressPOI.insert_one(jsonData)


def getBaiduAddress(latitude, longtitude):
    geoAddressURL = 'http://api.map.baidu.com' + \
        getPostURL(latitude, longtitude)
    logger.debug('URL: ' + geoAddressURL)
    r = session.get(geoAddressURL)
    logger.debug('baidu address ' + str(r.json()))
    # time.sleep(3)
    return r.json()


def getPostURL(latitude, longtitude):
    queryStr = '/geocoder/v2/?' + 'location=' + latitude + \
        ',' + longtitude + '&output=json&ak=' + baiduAK

    encodedStr = urllib.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")

    rawStr = encodedStr + baiduSK

    sn = hashlib.md5(urllib.quote_plus(rawStr)).hexdigest()
    URL = queryStr + '&sn=' + sn
    logger.debug('URL is: ' + URL)

    return URL


def main():
    client = MongoClient('localhost', 27017)
    db = client.truckDB
    truckInfo = db.truckInfo
    address = dict()
    for itor in truckInfo.find({}):
        # print itor
        # logger.debug(itor)
        itor['lat'] = float(itor['lat'])
        itor['lng'] = float(itor['lng'])
        truckInfo.save(itor)
        logger.info('rounded address is: ' + str(address))

    for addr in address:
        logger.info('rounded address is: ' + str(addr))
        #jsonData = getBaiduAddress(addr['latitude'], addr['longtitude'])
        #insertDB(db, jsonData)


session = requests.session()

main()
