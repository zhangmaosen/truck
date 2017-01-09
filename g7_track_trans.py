from pymongo import MongoClient
import os
import json
import io
import logging
import datetime
import time
import baidugeo
import pdb
import math

# tt = {'name': 'maosen'}

# truckInfo.insert_one(tt)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger()
PWD = os.getcwd()
TEST = '/test'
# '/test'
trucks_track_data_dir = PWD + TEST + '/trucks_track_data'
trucks_track_trans_data_dir = PWD + TEST + '/trucks_track_trans_data'
truckNo = dict()


def open_dst_fn(truck_no):
    # date = math.trunc(time.time())

    if(not os.path.exists(trucks_track_trans_data_dir)):
        os.mkdir(trucks_track_trans_data_dir)
    fn = io.open(trucks_track_trans_data_dir + '/truck_' +
                 truck_no + '.json', 'w', encoding='utf-8')
    return fn


def calc_delta(s_value, e_value, s_time, e_time):
    dt = e_time - s_time
    if(dt == 0):
        return 0
    else:
        dv = e_value - s_value
        g = float(dv) / dt
    return g


def calc_accelerate(s_speed, e_speed, s_time, e_time):
    dt = e_time - s_time
    if(dt == 0):
        return 0
    else:
        ds = e_speed - s_speed
        G = ds / dt
    return G


def get_truck_no(file_name):
    info = file_name.split('_')
    return info[1]


def trans_track_data():

    # open dst files, per truck per file
    dst_fns = {}
    for f in os.listdir(trucks_track_data_dir):
        truck_no = get_truck_no(f)
        if truck_no not in dst_fns:
            dst_fns[truck_no] = open_dst_fn(truck_no)
    # get srt files, per truck files
    srt_fns = {}
    for f in os.listdir(trucks_track_data_dir):
        truck_no = get_truck_no(f)
        if truck_no not in srt_fns:
            srt_fns[truck_no] = []
            srt_fns[truck_no].append(f)
        else:
            srt_fns[truck_no].append(f)
    srt_fns[truck_no].sort()

    for truck_no in srt_fns:
        dst_fn = dst_fns[truck_no]
        for f in srt_fns[truck_no]:
            logger.warning('open data file:' + trucks_track_data_dir + '/' + f)
            ff = io.open(trucks_track_data_dir + '/' + f, 'r', encoding='utf8')
            last_track = {}
            for line in ff.readlines():
                track = json.loads(line)
                track.pop('door', None)
                track.pop('temperature', None)
                track.pop('compressor', None)
                track.pop('acc', None)
                track.pop('icon', None)
                track.pop('time', None)
                logger.info(str(track))

                if last_track == {}:
                    avg_speed = {'avg_speed': 0}
                    track.update(avg_speed)

                    delta_steer = {'delta_steer': 0}
                    track.update(delta_steer)

                    accelerate = {'accelerate': 0}
                    track.update(accelerate)

                else:
                    avg_speed['avg_speed'] = calc_delta(
                        s_value=0,
                        e_value=track['distance'] / 100.0,
                        s_time=last_track['timestamp'],
                        e_time=track['timestamp'])
                    track.update(avg_speed)

                    delta_steer['delta_steer'] = calc_delta(
                        s_value=last_track['course'],
                        e_value=track['course'],
                        s_time=last_track['timestamp'],
                        e_time=track['timestamp'])
                    track.update(delta_steer)

                    accelerate['accelerate'] = calc_delta(
                        s_value=last_track['avg_speed'],
                        e_value=track['avg_speed'],
                        s_time=last_track['timestamp'] / 2.0,
                        e_time=track['timestamp'] / 2.0)
                    track.update(accelerate)
                truck_no_dict = {'truck_no': truck_no}
                track.update(truck_no_dict)
                dst_fn.write(unicode(json.dumps(track)))
                dst_fn.write(unicode('\n'))
                last_track = track
        dst_fn.close()


trans_track_data()
