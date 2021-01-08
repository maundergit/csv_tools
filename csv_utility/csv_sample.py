#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_sample.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-10-19 17:59:32>
# Licence:
#  Copyright (c) 2021 Masaharu N. Akei
#
#  This software is released under the MIT License.
#    http://opensource.org/licenses/mit-license.php
# ----------------------------------------------------------------------
import argparse
import textwrap
import sys

import re
import random
import pandas as pd

VERSION = 1.0


def init():
    arg_parser = argparse.ArgumentParser(description="derive sample records from big csv file",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
example:
  csv_sample.py --random --range=0.25,0.75 --output=test.csv big_sample_arb.csv 300

'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument("--range", dest="RANGE", help="range for sampling: [0,1.0]", type=str, metavar='START,END', default=None)
    arg_parser.add_argument("--random", dest="RANDOM", help="random sampling", action="store_true", default=False)
    arg_parser.add_argument("--skip", dest="RSKIP", help="skip sampling", type=int, metavar='INT', default=1)

    arg_parser.add_argument("--output", dest="OUTPUT", help="path of output file: default=stdout", type=str, metavar='FILE', default=None)

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='files to read, if empty, stdin is used')
    arg_parser.add_argument('sample_size', metavar='SAMPLE_SIZE', help='size of sample: ex 100 50%% 0.5', type=str)
    # arg_parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    # arg_parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    args = init()
    csv_file = args.csv_file
    d_range_s = args.RANGE
    r_mode = args.RANDOM
    r_skip = args.RSKIP
    s_size_s = args.sample_size

    output_file = args.OUTPUT

    if output_file is None:
        output_file = sys.stdout

    if d_range_s is not None:
        csv = re.split(r"\s*,\s*", d_range_s)
        d_range = [float(v) for v in csv]
        if any([v < 0 or v > 1.0 for v in d_range]):
            print("%Error:csv_sample:invalid range:{}".format(d_range_s), file=sys.stderr)
            sys.exit(1)
    else:
        d_range = [0, 1.0]

    print("%Inf:csv_sample:read csv file: {}".format(csv_file), file=sys.stderr)
    csv_df = pd.read_csv(csv_file)

    nrows = len(csv_df)
    if s_size_s.endswith("%"):
        s_size = int(float(s_size_s[:-1]) / 100 * nrows)
    elif float(s_size_s) < 1.0:
        s_size = int(float(s_size_s) / 100 * nrows)
    else:
        s_size = int(s_size_s)

    nr0 = int((nrows - 1) * d_range[0])
    nr1 = int((nrows - 1) * d_range[1])
    nrs = nr1 - nr0 + 1
    if nrs <= s_size:
        print("#warn:csv_sample:range {} was less than sample size:{}".format(d_range, s_size), file=sys.stderr)
        nr1 = nr0 + s_size - 1
    if nr1 >= nrows:
        print("#warn:csv_sample:range of sample [{},{}] was over data size:{}, sample size will be corrected to {}".format(
            nr0, nr1, nrows, nrows - nr0 + 1),
              file=sys.stderr)
        nr1 = nrows

    if r_mode and nr1 - nr0 + 1 > s_size:
        i_rows = random.sample(range(nr0, nr1 + 1), k=s_size)
    else:
        i_rows = list(range(nr0, nr0 + s_size))

    if r_skip > 1:
        i_rows = [i_rows[i] for i in range(0, len(i_rows), r_skip)]

    print("%Inf:csv_sample:do sampling {} records from {} records".format(len(i_rows), len(csv_df)), file=sys.stderr)
    o_df = csv_df.iloc[i_rows]

    o_df.to_csv(output_file)
