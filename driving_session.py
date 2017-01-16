#!/Users/xiaosen/Dev/python/bin/python
#!/Users/xiaosen/Dev/python/bin/python
import io
import os
import glob
import csv
import uuid
import sys
import logging
import pdb
import numpy as np


def get_six_point_poi(session_track):
    speed_list = session_track['speed']
    funcs = {'avg_speed': np.average,
             'median_speed': np.median,
             'min_speed': np.amin,
             'max_speed': np.amax}
    values = {}
    idx = {}

    for func in funcs:
        values[func] = funcs[func](speed_list)
        idx[func] = np.argmin(np.abs(speed_list - values[func]))


def seg_session(truck_file_name_pattern, session_window=15):
    session_window = int(session_window)
    for file_path_name in glob.glob(truck_file_name_pattern):

        start = True
        session_time = 0
        last_ts = 0

        logging.warning('read data file: %s', file_path_name)
        file_name = os.path.basename(file_path_name)
        out_file_name = file_name.split('.')[0] + '_session.csv'
        logging.warning('out data file_name: %s', out_file_name)
        with open(out_file_name, 'w') as csv_out_file:

            with open(file_path_name) as csvfile:
                session_id = str(uuid.uuid1())
                reader = csv.DictReader(csvfile)
                out_header = reader.fieldnames + ['session_id']
                writer = csv.DictWriter(csv_out_file, fieldnames=out_header)
                writer.writeheader()
                for row in reader:
                    # pdb.set_trace()
                    if start:
                        session_time = 0
                        last_ts = float(row['timestamp'])
                        start = False
                    else:
                        session_time = session_time + \
                            (float(row['timestamp']) - float(last_ts))
                        logging.debug('session_time is %d', session_time)
                    if session_time / 60 <= session_window:
                        row.update({'session_id': session_id})
                        writer.writerow(row)
                    else:
                        session_id = str(uuid.uuid1())
                        row.update({'session_id': session_id})
                        writer.writerow(row)
                        session_time = 0
                    last_ts = row['timestamp']


pattern = sys.argv[1]
window = sys.argv[2]
if len(sys.argv) > 3:
    if sys.argv[3] == 'v':
        logging.basicConfig(level=logging.DEBUG)
seg_session(pattern, window)
