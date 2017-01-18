#!/Users/xiaosen/Dev/python/bin/python
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


# logging.basicConfig(level=logging.WARNING)
geo_address_URL = 'http://api.map.baidu.com/geocoder/v2/'
# ak=E4805d16520de693a3fe707cdc962045&callback=renderReverse&location=39.983424,116.322987&output=json&pois=1
baiduAK = 'ki9OPCwL0o967ZHPgviMnDMCP3RwXIWZ'
baiduSK = '6a5Kg8e2z47ETsQHrsRU8GdfDZ6QKvoM'
params = dict()

# logging.basicConfig(filename='log.log', level=logging.DEBUG)
logger = logging.getLogger()


def get_baidu_address(latitude, longtitude):
    geo_address_URL = 'http://api.map.baidu.com' + \
        __get_post_URL__(latitude, longtitude)
    logger.debug('URL: ' + geo_address_URL)
    try:
        r = requests.get(geo_address_URL)
        logger.debug('baidu address ' + str(r.json()))
    except requests.exceptions.RequestException:
        logger.critical('baidu geo api exception ' +
                        str(requests.exceptions.RequestException))
        time.sleep(5)
        return get_baidu_address(latitude, longtitude)
    # time.sleep(3)
    return r.json()


def __get_post_URL__(latitude, longtitude):
    query_str = '/geocoder/v2/?' + 'location=' + latitude + \
        ',' + longtitude + '&output=json&ak=' + baiduAK

    encoded_str = urllib.quote(query_str, safe="/:=&?#+!$,;'@()*[]")

    rawStr = encoded_str + baiduSK

    sn = hashlib.md5(urllib.quote_plus(rawStr)).hexdigest()
    URL = query_str + '&sn=' + sn
    logger.debug('URL is: ' + URL)

    return URL
