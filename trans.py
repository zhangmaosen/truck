#!/Users/xiaosen/Dev/python/bin/python
from g7_track_trans import trans_track_data
import sys
import getopt
import logging
import io
import csv


def usage():
    print "-d --data_dir: data dir"
    print "-p --file_pattern: input file pattern"


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
    s_file_name = ''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd:p:", [
                                   "help",
                                   "data_dir=",
                                   "file_pattern="])
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
        elif o in ("-p", "--file_pattern"):
            s_file_name = a
        else:
            assert False, "unhandled option"
            sys.exit(2)
    # ...

    trans_track_data(data_dir=data_dir, file_pattern=s_file_name)


main()
