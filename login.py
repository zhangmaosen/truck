import logging
import requests
import io
import json
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth('jhn_admin', 'jhnBJ74110')
login = {'username':'jhn_admin','passwd':'jhnBJ74110'}
loginURL = 'http://g7s.ucenter.huoyunren.com/inside.php?t=json&m=login&f=userLogin'


# logging
logging.basicConfig(level=logging.DEBUG)
# files
tokenFile = io.open('token.txt', 'w', encoding='utf-8')

s = requests.session()

# get login token
r = s.post(loginURL, data=login)

_TOKEN = r.cookies['_TOKEN']
cookies = dict(_TOKEN=_TOKEN)

tokenFile.write(unicode(_TOKEN))
tokenFile.close()
