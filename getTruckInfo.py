import logging
import requests
import io
import json
import BeautifulSoup
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth('jhn_admin', 'jhnBJ74110')
# login = {'username':'jhn_admin','passwd':'jhnBJ74110'}
# loginURL =
# 'http://g7s.ucenter.huoyunren.com/inside.php?t=json&m=login&f=userLogin'
truckURL = 'http://g7s.truck.huoyunren.com/inside.php?t=json&m=map'

# files
# truckInfoFile = io.open('truckinfo', 'w', encoding='utf-8')
tokenFile = io.open('token.txt', 'r', encoding='utf-8')

# params
allTruckInfoParam = dict(f='getAllTruckInfo')
allTruckInfoForm = {'pageNo': '1', 'pageSize': '400', 'type': 'truck'}
truckHistParam = dict(f='gethistory')


def save2File(fileName, jsonData):
    f = io.open('truckInfoData/' + fileName, 'w', encoding='utf8')
    f.write(unicode(json.dumps(jsonData, indent=4, ensure_ascii=False)))
    f.close()


# logging
logging.basicConfig(level=logging.DEBUG)

s = requests.session()

# get login token
# r = s.post(loginURL, data=login)

_TOKEN = tokenFile.readline()
logging.info('read token is ' + _TOKEN)
cookies = dict(_TOKEN=_TOKEN)
# get all truck info

r = s.post(truckURL, data=allTruckInfoForm,
           params=allTruckInfoParam, cookies=cookies, auth=auth)
logging.info('get truckinfo pageNo: %d' % 1)
fileName = 'truckInfo%d.json' % 1
save2File(fileName=fileName, jsonData=r.json())

truckNum = int(r.json()['data']['totalCount'])
pageSize = 400
pageNum = truckNum // pageSize + 1

logging.info('truck number is %d ' % truckNum)
logging.info('form data is ' + allTruckInfoForm.__str__())

allTruckInfoForm['pageSize'] = pageSize

for itor in range(2, pageNum + 1):
    allTruckInfoForm['pageNo'] = itor
    logging.info('get truckinfo pageNo: %d' % itor)
    logging.info('form data is ' + allTruckInfoForm.__str__())
    r = s.post(truckURL, data=allTruckInfoForm,
               params=allTruckInfoParam, cookies=cookies, auth=auth)
    fileName = 'truckInfo%d.json' % itor
    save2File(fileName=fileName, jsonData=r.json())


# save truck info data


# get truck history
