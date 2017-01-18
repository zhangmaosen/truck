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
import baidu_geo
import unicode_csv


def get_poi(raw_poi):
    if raw_poi['result'] != []:
        city = raw_poi['result']['addressComponent']['city']
        street = raw_poi['result']['addressComponent']['street']
        address = raw_poi['result']['formatted_address']

    return {'city': city, 'street': street, 'address': address}


def get_four_point(session_tracks):
    speed_list = []
    for row in session_tracks:
        speed_list.append(float(row['speed']))
    funcs = {'avg_speed': np.average,
             'median_speed': np.median,
             'min_speed': np.amin,
             'max_speed': np.amax}
    values = {}
    idx = {}

    result = {}
    # pdb.set_trace()
    for func in funcs:
        values[func] = funcs[func](speed_list)
        i = idx[func] = np.argmin(np.abs(speed_list - values[func]))
        logging.debug('Nearest %s speed is %d', str(func), idx[func])
        poi = get_poi(
            baidu_geo.get_baidu_address(
                session_tracks[i]['lat'],
                session_tracks[i]['lng']))
        result.update({func + '_city': poi['city'].encode('utf8'),
                       func + '_street': poi['street'].encode('utf8'),
                       func + '_address': poi['address'].encode('utf8')})
    return result


def write_session_poi(csv_writer, session_tracks):
    poi = get_four_point(session_tracks)
    session_id = session_tracks[0]['session_id']
    ts = session_tracks[0]['timestamp']
    poi.update({'session_id': session_id, 'timestamp': ts})
    # pdb.set_trace()
    csv_writer.writerow(poi)


def pop_session(session_tracks):
    length = len(session_tracks)
    session = []
    session_id = str(uuid.uuid1())
    for i in range(length - 1):
        session_tracks[0].update({'session_id': session_id})
        session.append(session_tracks[0])
        session_tracks.remove(session_tracks[0])
    return session


def write_session(csv_writer, session_tracks):
    for row in session_tracks:
        csv_writer.writerow(row)


def seg_session2(truck_file_name_pattern, session_window=15):
    session_window = int(session_window)
    for file_path_name in glob.glob(truck_file_name_pattern):

        session_time = 0

        # make file name
        logging.warning('read data file: %s', file_path_name)
        file_name = os.path.basename(file_path_name).split('.')[0]
        # session main file
        out_file_name = file_name + '_session.csv'
        logging.warning('out data file_name: %s', out_file_name)
        # session poi file
        out_poi_name = file_name + '_session_poi.csv'
        logging.warning('out data file_name: %s', out_poi_name)

        with open(out_file_name, 'wb') as csv_out_file:
            with open(out_poi_name, 'wb') as csv_poi_file:

                with open(file_path_name) as csvfile:

                    reader = csv.DictReader(csvfile)

                    out_header = reader.fieldnames + ['session_id']
                    writer = csv.DictWriter(
                        csv_out_file, fieldnames=out_header)
                    writer.writeheader()

                    poi_header = ['session_id',
                                  'timestamp',
                                  'avg_speed_city',
                                  'avg_speed_street',
                                  'avg_speed_address',
                                  'median_speed_city',
                                  'median_speed_street',
                                  'median_speed_address',
                                  'max_speed_city',
                                  'max_speed_street',
                                  'max_speed_address',
                                  'min_speed_city',
                                  'min_speed_street',
                                  'min_speed_address']

                    poi_writer = csv.DictWriter(
                        csv_poi_file, fieldnames=poi_header)
                    poi_writer.writeheader()

                    session_tracks = []

                    row = reader.next()

                    if(row is not None):
                        session_tracks.append(row)

                    for row in reader:
                        # pdb.set_trace()
                        session_time = (float(row['timestamp']) -
                                        float(session_tracks[0]['timestamp']))
                        logging.debug('session_time is %d', session_time)

                        session_tracks.append(row)

                        if session_time / 60 > session_window:
                            session = pop_session(session_tracks)
                            write_session(writer, session)
                            write_session_poi(poi_writer, session)

                    if len(session_tracks) > 0:
                        session_tracks.append({})
                        session = pop_session(session_tracks)
                        write_session(writer, session)
                        write_session_poi(poi_writer, session)


pattern = sys.argv[1]
window = sys.argv[2]
if len(sys.argv) > 3:
    if sys.argv[3] == 'v':
        logging.basicConfig(level=logging.DEBUG)
seg_session2(pattern, window)
