import json2csv
import os
import json
import io
import logging
import glob
import pdb

# tt = {'name': 'maosen'}

# truckInfo.insert_one(tt)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger()


def close_fs(fs):
    for truck_no in fs:
        for file in fs[truck_no]:
            file.close()


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


def get_files(truck_nos, data_dir, open_type, file_format='json'):
    fns = {}
    if open_type == 'w':
        for truck_no in truck_nos:
            fn = data_dir + 'truck_' + truck_no + '.' + file_format
            f = io.open(fn, open_type, encoding='utf8')
            logging.warning('open truck data file for trans: %s', fn)
            fns.update({truck_no: [f]})
    elif open_type == 'r':

        for truck_no in truck_nos:

            rfns = sorted(glob.glob(data_dir + 'track_' + truck_no + '*'))
            rfs = []
            for fn in rfns:
                f = io.open(fn, open_type, encoding='utf8')
                logging.warning('open track data file: %s', fn)
                rfs.append(f)

            fns.update({truck_no: rfs})
    return fns


def get_truck_nos(dir_pattern_list):
    fns = glob.glob(dir_pattern_list)
    truck_nos = {}
    for fn in fns:
        t = fn.split('/')
        file_name = t[len(t) - 1]
        truck_no = get_truck_no(file_name)
        if truck_no not in truck_nos:
            truck_nos.update({truck_no: '1'})
    return truck_nos


def get_truck_no(file_name):
    info = file_name.split('_')
    return info[1]


def format_convert(input_file_name, output_file_name, to_format='csv'):
    if to_format == 'csv':
        logging.warning('file format trans: %s to %s',
                        input_file_name, output_file_name)
        json2csv.json2csv(input_file_name, output_file_name)


def convert2csv(truck_nos, data_dir):
    for truck_no in truck_nos:
        ifn = data_dir + 'truck_' + truck_no + '.json'
        ofn = data_dir + 'truck_' + truck_no + '.csv'
        format_convert(ifn, ofn, 'csv')


def trans_track_data(data_dir, file_pattern='*'):
    PWD = os.getcwd()
    # '/test'
    input_data_dir = PWD + '/' + data_dir + \
        '/trucks_track_data/'
    output_data_dir = PWD + '/' + \
        data_dir + '/trucks_track_trans_data/'

    truck_nos = get_truck_nos(input_data_dir + file_pattern)

    # open dst files, per truck per file
    src_fs = get_files(truck_nos, input_data_dir, 'r', 'json')
    dst_fs = get_files(truck_nos, output_data_dir, 'w', 'json')

    for truck_no in src_fs:
        for dst_fn in dst_fs[truck_no]:
            for ff in src_fs[truck_no]:
                logger.warning('open data file:' + ff.name)

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

                        delta_time = {'delta_time': 0}
                        track.update(delta_time)

                        curve = {'curve': 0}
                        track.update(curve)

                    else:
                        avg_speed['avg_speed'] = calc_delta(
                            s_value=0,
                            e_value=track['distance'] / 100.0,
                            s_time=last_track['timestamp'],
                            e_time=track['timestamp']) * 3.6
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
                            s_time=last_track['timestamp'] / 1.0,
                            e_time=track['timestamp'] / 1.0)
                        track.update(accelerate)

                        curve['curve'] = None
                        delta_course = abs(
                            last_track['course'] - track['course'])
                        if delta_course > 180:

                            delta_course = 360 - delta_course

                        if delta_course == 0:
                            curve['curve'] = float("inf")
                        else:
                            curve['curve'] = track[
                                'distance'] / float(delta_course)
                        track.update(curve)

                        delta_time['delta_time'] = int(track['timestamp']) - \
                            int(last_track['timestamp'])
                        track.update(delta_time)

                    truck_no_dict = {'truck_no': truck_no}
                    track.update(truck_no_dict)
                    dst_fn.write(unicode(json.dumps(track)))
                    dst_fn.write(unicode('\n'))
                    last_track = track
    close_fs(dst_fs)
    close_fs(src_fs)

    convert2csv(truck_nos, output_data_dir)
