from pymongo import MongoClient
import os
import json
import io
import logging

client = MongoClient('localhost', 27017)
db = client.truckDB

truckInfo = db.truckInfoNew

# tt = {'name': 'maosen'}

# truckInfo.insert_one(tt)

PWD = os.getcwd()
truckDataFiles = PWD + '/truckHistData'
logging.warning('get file from: ' + truckDataFiles)
truckNo = dict()

for f in os.listdir(truckDataFiles):
    ff = io.open(truckDataFiles + '/' + f, 'r', encoding='utf8')
    jsonData = json.load(ff)
    logging.debug(str(jsonData))

    truckNo['carnum'] = jsonData['data']['result']['carnum']
    details = jsonData['data']['result']['detail']

    for detail in details:
        detail.update(truckNo)
        truckInfo.insert_one(detail)

