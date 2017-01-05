import logging
import requests
import io
import json
import os
import time
import datetime
import urllib
import pdb


from requests.auth import HTTPBasicAuth
# logging.basicConfig(level=logging.WARNING)
truckInfoFile = 'truckInfoDataTest'
# truckInfoFile = 'truckInfoData'
truckHistFile = 'truckHistDataTest'
checkPointFile = '_checkPoint'

auth = HTTPBasicAuth('jhn_admin', 'jhnBJ74110')
tokenFile = io.open('token.txt', 'r', encoding='utf-8')
_TOKEN = tokenFile.readline()
logging.info('read token is ' + _TOKEN)
cookies = dict(_TOKEN=_TOKEN)

nTimes = 100
pageSize = 1000
delta = datetime.timedelta(days=1)

# login = {'username':'jhn_admin','passwd':'jhnBJ74110'}
# loginURL =
# 'http://g7s.ucenter.huoyunren.com/inside.php?t=json&m=login&f=userLogin'
truckURL = 'http://g7s.truck.huoyunren.com/inside.php?t=json&m=map&f=gethistory'

session = requests.session()

# files
tokenFile = io.open('token.txt', 'r', encoding='utf-8')
token = tokenFile.readline()
cookies = dict(_TOKEN=_TOKEN)


def getCheckPoint(truckNo):
    fn = truckNo + checkPointFile
    if os.path.exists(fn):
        f = io.open(truckNo + checkPointFile, 'r')
        cp = json.load(f)
        ts = cp['checkTime']
        itor = cp['itor']
        ts = datetime.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S.%f')
        ccp = {'checkTime': ts, 'itor': itor}
    else:
        ccp = {'checkTime': datetime.datetime.now(), 'itor': 0}
    return cpp


def saveCheckPoint(truckNo, checkTime, itor):
    f = io.open(truckNo + checkPointFile, 'w', encoding='utf-8')
    cp = {'checkTime': checkTime, 'itor': itor}
    f.write(unicode(json.dump(dict)))
    f.close()


def save2File(fileName, jsonData):
    f = io.open(truckHistFile + '/' + fileName, 'w', encoding='utf8')
    f.write(unicode(json.dumps(jsonData, indent=4, ensure_ascii=False)))
    f.close()


def getAllTruckInfoFile(fileName):
    return os.listdir(os.getcwd() + '/' + fileName)


def isNoData(jsonData):
    # pdb.set_trace()
    if 'sharetime' in jsonData['data']['result']:
        return True
    else:
        return False


def getFormData(truckNo, truckInfo):
    formData = dict()
    formData['searchtype'] = 'truckid'
    formData['searchid'] = truckInfo['truckid']
    formData['searchno'] = truckNo
    formData['spacing'] = '1'
    formData['carnum'] = truckInfo['carnum'].encode('utf8')
    formData['bmode'] = 'true'
    formData['detailtype'] = 'json'
    formData['pageSize'] = pageSize
    formData['requestNewFunc'] = '1'
    return formData


def getAllAjaxData(formData, startTime, endTime):
    r = getAjaxData(formData, startTime, endTime)
    detail = r['data']['result']['detail']
    if len(detail) == pageSize:
        startTime = datetime.datetime.fromtimestamp(
            detail[pageSize - 1]['timestamp'])
        tt = getAllAjaxData(formData, startTime, endTime)
        detail.extend(tt['data']['result']['detail'])
    r['data']['result']['detail'] = detail
    return r


def getAjaxData(formData, startTime, endTime):
    formData['begintime'] = startTime
    formData['endtime'] = endTime
    urlparam = urllib.urlencode(formData)
    logging.warning('get hist form data is ' + urlparam)

    r = session.post(truckURL, data=formData, cookies=cookies, auth=auth)

    return r.json()


def getHistData(truckNo, truckInfo, startTime, nTimes, cp):
    formData = getFormData(truckNo, truckInfo)

    lastTime = startTime

    for itor in range(cp['itor'], nTimes):
        st = lastTime - delta
        et = lastTime
        formData['begintime'] = st
        formData['endtime'] = et

        truckData = getAllAjaxData(formData, st, et)
        saveCheckPoint(truckNo, st)
        # pdb.set_trace()
        time.sleep(1)
        logging.debug('get ajax data' + str(truckData))
        if(isNoData(truckData)):
            logging.warning('no data get!')
            break
        save2File('truck_' + truckNo + '_' + str(itor), truckData)
        lastTime = st


files = getAllTruckInfoFile(truckInfoFile)

logging.info('read list files: ' + ' '.join(files))


for file in files:
    logging.info('read truckinfo from file: ' + file)
    data = io.open(truckInfoFile + '/' + file, 'r', encoding='utf8')
    jsonData = json.load(data)

    trucksInfo = jsonData['data']['result']

    for iid in trucksInfo:
        cp = getCheckPoint(truckNo=iid)
        logging.warning(iid + ' get data start at' + str(cp['checkTime']))
        getHistData(iid, trucksInfo[iid], sTime, nTimes, cp)
 # save truck info data


# get truck history
