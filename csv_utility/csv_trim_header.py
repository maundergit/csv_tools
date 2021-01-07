#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_trime_header.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-08-15 09:15:18>
# Licence:
#  Copyright (c) 2021 Masaharu N. Akei
#
#  This software is released under the MIT License.
#    http://opensource.org/licenses/mit-license.php
# ----------------------------------------------------------------------
import argparse
import fileinput
import textwrap
import io
import csv
import sys
import numpy as np

VERSION = 1.0


def init():
    arg_parser = argparse.ArgumentParser(description="DEPRICATED:for csv file, to derive column names in one row from ones in multi rows",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:
  this script was deprectaed. use 'csv_multiindex_columns.py'.

example:

  csv_trim_header.py --rows=2 test_trim_header.csv
A1_B1,A1_B2,A2_B3,A2_B4,A3_B5,A3_B6,A3_B7,A3_B8

  csv_trim_header.py --rows=2 --add_column_index test_trim_header.csv
A1_B1_00000,A1_B2_00001,A2_B3_00002,A2_B4_00003,A3_B5_00004,A3_B6_00005,A3_B7_00006,A3_B8_00007

cat test_trim_header.csv
A1,,A2,,A3,,
B1,B2,B3,B4,B5,B6,B7,B8


'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument("--rows", dest="NROWS", help="number of header rows: default=1", type=int, metavar='INT', default=1)
    arg_parser.add_argument("--add_column_index", dest="ADDINDEX", help="add index to column name", action="store_true", default=False)

    arg_parser.add_argument('file', metavar='CSV_FILE', help='files to read, if empty, stdin is used')

    args = arg_parser.parse_args()
    return args


def read_headers(csv_file, nrows):
    """read csv file and fill empty columns by forward method along row-axis

    :param csv_file: 
    :returns: 
    :rtype: 

    """

    # read csv file
    strout = io.StringIO()
    lno = 0
    for line in fileinput.input(files=csv_file):
        # print(">>" + line)
        line = line.rstrip()
        strout.write(line + "\n")
        lno += 1
        if lno > nrows - 1:
            break

    strout.seek(0)
    csv_reader = csv.reader(strout)

    # fill empty columns by forward method
    records = []
    nf = 0
    for rec in csv_reader:
        if nf < len(rec):
            nf = len(rec)
        v1 = ""
        for i, cv in enumerate(rec):
            if cv is not None and len(cv) > 0:
                v1 = cv
            rec[i] = v1
        records.append(rec)

    return records, nf


if __name__ == "__main__":
    print("#warn:csv_trim_header: this is depricated. use 'csv_multiindex_columns'.", file=sys.stderr)
    args = init()
    csv_file = args.file
    nrows = args.NROWS
    addindex = args.ADDINDEX

    records, nf = read_headers(csv_file, nrows)

    # if number of columns was insufficient, missing columns are filled with last column
    lno = 0
    for i, rec in enumerate(records):
        lno += 1
        if len(rec) < nf:
            print("#warn:csv_trim_header:insufficient number of columns:row={}".format(lno), file=sys.stderr)
            records[i] = rec + [rec[-1]] * (nf - len(rec))

    if nrows > 1:
        headers_t = np.array(records)
        headers_t = np.array(records, dtype=str).T.tolist()
        headers_1d = list(map(lambda x: "_".join(x), headers_t))
    else:
        headers_1d = records  # type: ignore

    if addindex:
        headers_1d = ["{}_{:05d}".format(v, i) for i, v in enumerate(headers_1d)]

    csv_writer = csv.writer(sys.stdout)
    csv_writer.writerow(headers_1d)
