import logging
import requests
import io
import json
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth('jhn_admin', 'jhnBJ74110')
login = {'username':'jhn_admin','passwd':'jhnBJ74110'}
loginURL = 'http://g7s.ucenter.huoyunren.com/inside.php?t=json&m=login&f=userLogin'
truckURL = 'http://g7s.truck.huoyunren.com/inside.php?t=json&m=map'

allTruckInfoParam = dict(f='getAllTruckInfo')
allTruckInfoForm = {'pageNo':'1', 'pageSize':'400', 'type':'truck'}
truckHistParam = dict(f='gethistory')

# logging
logging.basicConfig(level=logging.DEBUG)
# files
truckInfoFile = io.open('truckinfo.txt', 'w', encoding='utf-8')

s = requests.session()

# get login token
r = s.post(loginURL, data=login)

_TOKEN = r.cookies['_TOKEN']
cookies = dict(_TOKEN=_TOKEN)
#get all truck info

r = s.post(truckURL, params = allTruckInfoParam, cookies = cookies, auth = auth)
truckInfoFile.write(unicode(json.dumps(r.json(), ensure_ascii=False)))

truckNum = int(r.json()['data']['totalCount'])
pageSize = 400
pageNum = truckNum//pageSize + 1

logging.info('truck number is %d ' % truckNum)
logging.info('form data is ' + allTruckInfoForm.__str__())

allTruckInfoForm['pageSize'] = pageSize

for itor in range(2, pageNum+1):
    logging.info('get truckinfo pageNo: %d' % itor)
    logging.info('form data is ' + allTruckInfoForm.__str__())
    allTruckInfoForm['pageNo'] = itor
    r = s.post(truckURL, data = allTruckInfoForm, params = allTruckInfoParam, cookies = cookies, auth = auth)
    truckInfoFile.write(unicode(json.dumps(r.json(), ensure_ascii=False)))


#save truck info data


#get truck history



