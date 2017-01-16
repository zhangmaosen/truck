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
import sys
import getopt
import pickle


class G7Login:
    url = 'http://g7s.ucenter.huoyunren.com/inside.php?t=json&m=login&f=userLogin'
    __passwd = 'jhnBJ74110'
    __username = 'jhn_admin'
    __auth = ''
    __token = dict()
    __session = ''

    __time_out = 10
    __instance = None

    __token_file_name = "token.txt"

    def __new__(self, *args, **kwargs):
        if G7Login.__instance is None:
            G7Login.__instance = object.__new__(self, *args, **kwargs)
        return G7Login.__instance

    def __init__(self):
        self.get_token()
        self.__auth = HTTPBasicAuth(self.__username, self.__passwd)

    def post_url(self, url, params=None, form_data=None):
        r = requests.session().post(url, data=form_data, params=params,
                                    cookies=self.__token, auth=self.__auth)
        return r.json()

    def get_token(self):

        if os.path.exists(self.__token_file_name):
            fn = io.open(self.__token_file_name, 'r', encoding='utf-8')
            line = fn.readline()
            logging.debug('read line: ' + line)
            self.__token = json.loads(line)
            logging.debug('get token is: ' + str(self.__token))
            fn.close()
        else:
            login = {'username': self.__username, 'passwd': self.__passwd}
            s = self.session = requests.session()
            r = s.post(self.url, data=login)
            self.__token = dict(_TOKEN=r.cookies['_TOKEN'])
            fn = io.open(self.__token_file_name, 'w', encoding='utf-8')
            fn.write(unicode(json.dumps(self.__token)))
            fn.close()


class CrawlerJobProgress:
    progress = {}
    file_name = ''
    progress_name = ''
    l_time = ''

    def __init__(self,
                 name="crawler_job",
                 l_time=str(datetime.datetime.now())):
        self.progress_name = name
        self.file_name = name + '_progress' + '.json'
        self.l_time = str(l_time)

    def update_progress(self, truck, start_time, end_time):
        truck_no = truck['truck_no']
        s_t = dict()
        e_t = dict()
        s_t['start_time'] = str(start_time)
        e_t['end_time'] = str(self.l_time)
        self.progress.update({truck_no: {}})
        self.progress[truck_no].update(s_t)
        self.progress[truck_no].update(e_t)
        f = io.open(self.file_name, 'w', encoding='utf8')
        f.write(unicode(json.dumps(self.progress, indent=4)))
        f.close()


class G7DataCrawler():
    progress = ''
    # TEST dir
    Dir = 'test'

    # for truck crawler
    truck_url = 'http://g7s.truck.huoyunren.com/inside.php?t=json&m=map'
    trucks_info_param = dict(f='getAllTruckInfo')
    trucks_info_form = {'pageNo': '1', 'pageSize': '400', 'type': 'truck'}
    trucks_info_data_dir = ''
    # for track crawler

    trucks_track_param = dict(f='gethistory')
    trucks_track_form = dict()
    trucks_track_data_dir = ''

    #
    trucks_track_file_prefix = 'track_'

    # check point
    trucks_track_check_point_fn = ''

    def __get_date(self):
        date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
        return date

    def save_data(self, fn, json_data):
        fn.write(unicode(json.dumps(json_data)))
        fn.write(unicode('\n'))

    def make_data_dir(self, data_dir):
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)

    def __init__(self, data_dir=None):
        if data_dir is not None:
            self.Dir = 'data'
        self.trucks_info_data_dir = data_dir + '/trucks_info_data/'
        # for track crawler
        self.trucks_track_data_dir = data_dir + '/trucks_track_data/'
        self.make_data_dir(self.trucks_info_data_dir)
        self.make_data_dir(self.trucks_track_data_dir)

    def crawl_fleets_info(self, g7_login):
        fn = io.open(self.trucks_info_data_dir +
                     'fleets_info.json', 'w', encoding='utf8')
        fleets_count = self.crawl_fleets_count(g7_login)
        page_num = fleets_count // 400 + 1
        for pager in range(1, page_num + 1):
            self.trucks_info_form['pageNo'] = pager
            r = g7_login.post_url(
                self.truck_url,
                params=self.trucks_info_param,
                form_data=self.trucks_info_form)
            rt = r['data']['result']
            for itor in rt:
                truck = dict()
                truck['truck_no'] = itor
                truck.update(rt[itor])
                self.save_data(fn, truck)
        fn.close()

    def crawl_fleets_count(self, g7_login):
        self.trucks_info_form['pageNo'] = 1
        r = g7_login.post_url(
            self.truck_url,
            params=self.trucks_info_param,
            form_data=self.trucks_info_form)
        fleets_count = r.json()['data']['totalCount']
        self.fleets_cnt = int(fleets_count)
        return int(fleets_count)

    def crawl_trucks_track(self, g7_login,
                           n_delta=1, l_time=None, sample_truck=None):
        self.progress = CrawlerJobProgress(
            'track_data_crawler_' + str(l_time), l_time)
        for file in os.listdir(self.trucks_info_data_dir):
            fn = self.trucks_info_data_dir + file
            logging.warning('truck info file name is: ' + fn)
            f = io.open(fn, 'r', encoding='utf-8')
            for line in f.readlines():

                truck = dict()
                logging.warning('truck info is: ' + line)
                truck = json.loads(line)

                if l_time is None:
                    last_time = datetime.datetime.now()
                else:
                    last_time = datetime.datetime.strptime(
                        l_time, '%Y-%m-%d')

                if sample_truck is not None:
                    logging.warning("sample crawling begin!")
                    if truck['truck_no'] in sample_truck:
                        logging.warning("crawl sample truck " +
                                        truck['truck_no'] + "\'s track data")
                        self.crawl_truck_all_track(
                            g7_login, truck, n_delta=n_delta,
                            last_time=last_time)
                else:
                    self.crawl_truck_all_track(
                        g7_login, truck, n_delta=n_delta, last_time=last_time)
            f.close()

    # def crawl_trucks_track_check_point(self, )
    def crawl_truck_all_track(self, g7_login, truck, n_delta=1,
                              last_time=datetime.datetime.now()):
        delta = datetime.timedelta(days=1)

        for i in range(n_delta):
            s_time = last_time - delta
            e_time = last_time

            fn = self.trucks_track_data_dir + \
                self.trucks_track_file_prefix + \
                truck['truck_no'] + '_' + \
                last_time.strftime("%Y_%m_%d_%H_%M") + '.json'

            r = self.crawl_truck_track(
                g7_login=g7_login, truck=truck, s_time=s_time, e_time=e_time)
            if r is None:
                break

            tracks = r['data']['result']['detail']
            if tracks != []:
                f = io.open(fn, 'w', encoding='utf8')
                for track in tracks:
                    self.save_data(f, track)
                f.close()
            # save progress of crawler job
            self.progress.update_progress(truck, s_time, e_time)
            last_time = s_time

    def crawl_truck_track(self, g7_login, truck,
                          s_time, e_time, page_size=1000):
        self.set_trucks_track_form(
            g7_login=g7_login, truck=truck, s_time=s_time, e_time=e_time)
        r = g7_login.post_url(
            self.truck_url,
            params=self.trucks_track_param,
            form_data=self.trucks_track_form)
        logging.debug('truck track data: ' + str(r))

        if 'data' in r:
            detail = r['data']['result']['detail']
        else:
            logging.critical('data crawl wrong! response is: ' + str(r))
            return None
        if len(detail) == page_size:
            s_time = datetime.datetime.fromtimestamp(
                detail[page_size - 1]['timestamp'])
            tt = self.crawl_truck_track(g7_login, truck, s_time, e_time)
            detail.extend(tt['data']['result']['detail'])
        r['data']['result']['detail'] = detail
        return r

    def set_trucks_track_form(self, g7_login, truck, type='json',
                              page_size=1000, spacing=1,
                              s_time=None, e_time=None):

        self.trucks_track_form['searchtype'] = 'truckid'
        self.trucks_track_form['searchid'] = truck['truckid']
        self.trucks_track_form['searchno'] = truck['truck_no']
        self.trucks_track_form['carnum'] = truck['carnum'].encode('utf8')

        self.trucks_track_form['spacing'] = spacing
        self.trucks_track_form['bmode'] = 'true'
        self.trucks_track_form['detailtype'] = type
        self.trucks_track_form['pageSize'] = page_size
        self.trucks_track_form['requestNewFunc'] = '1'

        self.trucks_track_form['begintime'] = s_time
        self.trucks_track_form['endtime'] = e_time
