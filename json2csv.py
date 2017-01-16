#!/Users/xiaosen/Dev/python/bin/python
import json
import io
import sys


def json2csv(i_fn, o_fn):

    i_f = io.open(i_fn, 'r')
    o_f = io.open(o_fn, 'w')

    line = i_f.readline()
    j_data = json.loads(line)
    is_line_header = True
    for itor in j_data:

        if is_line_header:
            o_f.write(unicode(str(itor)))
            is_line_header = False
        else:
            o_f.write(unicode(',' + str(itor)))
    o_f.write(unicode("\n"))
    i_f.close()

    i_f = io.open(i_fn, 'r')

    for line in i_f.readlines():
        j_data = json.loads(line)

        is_line_header = True
        for itor in j_data:

            if is_line_header:
                o_f.write(unicode(str(j_data[itor])))
                is_line_header = False
            else:
                o_f.write(unicode(',' + str(j_data[itor])))
        o_f.write(unicode("\n"))
        is_line_header = True

    i_f.close()
    o_f.close()
