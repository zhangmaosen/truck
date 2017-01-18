#!/Users/xiaosen/Dev/python/bin/python
from g7_data_crawler import G7Login, G7DataCrawler
import sys
import getopt
import logging
import io
import pdb
import csv


def usage():
    print "-d --data_dir: data dir"
    print "-t --start_time: crawl time start at"
    print "-c --crawl_days: crawl N days data"
    print "-s --sample_truck_file: sample truck no"
    print "-j --job_file_name:crawl job"


def load_crawl_job(fname):
    crawl_jobs = []
    logging.warning('begin load crawl job file %s', fname)
    with open(fname, 'rb') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            crawl_jobs.append(row)
    return crawl_jobs


def load_sample_trucks(fname, is_header=False):
    logging.warning("load sample trucks begin! file name is " + fname)
    f = io.open(fname, 'r', encoding='utf8')
    trucks = []
    if is_header:
        f.readline()
    for line in f.readlines():
        line.rstrip('\n')
        info = line.split('\t')
        trucks.append(info[0])
    logging.warning("load sample trucks over!")
    return trucks


def main():
    data_dir = ''
    start_time = ''
    crawl_days = 0
    s_file_name = ''
    job_file_name = ''
    crawl_jobs = []
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd:t:c:s:j:", [
                                   "help", "start_time=",
                                   "data_dir=", "crawl_days=",
                                   "sample_truck_file=",
                                   "job_file="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    if len(opts) == 0:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-d", "--data_dir"):
            data_dir = a
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-t", "--start_time"):
            start_time = a
        elif o in ("-c", "--crawl_days"):
            crawl_days = int(a)
        elif o in ("-s", "--sample_truck_file"):
            s_file_name = a
        elif o in ("-j", "--job_file"):
            job_file_name = a
        else:
            assert False, "unhandled option"
            sys.exit(2)
    # ...
    g7_login = G7Login()
    if job_file_name != '':
        crawl_jobs = load_crawl_job(job_file_name)
    else:
        trucks = load_sample_trucks(s_file_name)
        logging.debug(str(g7_login))

    for job in crawl_jobs:
        data_dir = job['data_dir']
        start_time = job['start_time']
        crawl_days = job['crawl_days']
        trucks = [job['truck_no']]
        g7_crawler = G7DataCrawler(data_dir)
        g7_crawler.crawl_trucks_track2(
            g7_login, l_time=start_time,
            n_delta=int(crawl_days), sample_truck=trucks)


main()
