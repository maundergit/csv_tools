#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_window_rolling.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-11-07 14:54:28>
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
import pandas as pd

VERSION = 1.0

WINDOW_TYPES = ["boxcar", "triang", "blackman", "hamming", "bartlett", "parzen", "bohman", "blackmanharris", "nuttall", "barthann"]

FUNC_TABLES = ["sum", "min", "max", "mean", "median", "std", "count", "var", "skew", "kurt", "corr", "cov"]


def init():
    arg_parser = argparse.ArgumentParser(description="do rolling columns data, like as moving-average",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:
   If window_type is not None, only one of ["sum", "mean", "var", "std"] is abailable as window_function. 

example:
  csv_window_rolling.py big_sample_rand.csv COL_0000 20
  csv_window_rolling.py --window_type=boxcar --window_function=std big_sample_rand.csv COL_0000 20


'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))

    arg_parser.add_argument("--index",
                            dest="IDXCOL",
                            help="column of independent values, default=id of rows",
                            type=str,
                            metavar='COLUMN',
                            default=None)
    arg_parser.add_argument("--window_type", dest="WTYPE", help="type of window function", choices=WINDOW_TYPES, default=None)
    arg_parser.add_argument("--window_function", dest="WFUNC", help="function to do", choices=FUNC_TABLES, default="sum")

    arg_parser.add_argument("--output_file",
                            dest="OUTPUT",
                            help="path of output file, default=stdout",
                            type=str,
                            metavar='FILE',
                            default=sys.stdout)

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='files to read, if empty, stdin is used')
    arg_parser.add_argument('columns', metavar='COLUMN[,COLUMN..]', type=str, help='columns to process')
    arg_parser.add_argument('window_size', metavar='INT', type=int, help='size of window')
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    args = init()
    csv_file = args.csv_file
    output_file = args.OUTPUT

    columns_s = args.columns
    columns = re.split(r"\s*,\s*", columns_s)
    w_size = args.window_size

    idx_col = args.IDXCOL
    w_type = args.WTYPE
    w_func = args.WFUNC

    if w_type is not None:
        if w_func not in ["sum", "mean", "var", "std"]:
            print("??error:csv_window_rolling:invalid combination window_type and window_function:{},{}".format(w_type, w_func),
                  file=sys.stderr)
            sys.exit(1)

    if csv_file == "-":
        csv_file = sys.stdin

    csv_df = pd.read_csv(csv_file)

    r_params = {"center": True}
    if idx_col is not None:
        r_params.update({"on": idx_col})
    for cn in columns:
        cn2 = cn + "_S{}T{}F{}".format(w_size, w_type, w_func)
        ds = csv_df[cn].rolling(w_size, win_type=w_type, **r_params)

        if w_func == "sum":
            csv_df[cn2] = ds.sum(numeric_only=True)
        elif w_func == "mean":
            csv_df[cn2] = ds.mean(numeric_only=True)
        elif w_func == "var":
            csv_df[cn2] = ds.var(numeric_only=True)
        elif w_func == "std":
            csv_df[cn2] = ds.std(numeric_only=True)
        elif w_func == "min":
            csv_df[cn2] = ds.min(numeric_only=True)
        elif w_func == "max":
            csv_df[cn2] = ds.max(numeric_only=True)
        elif w_func == "median":
            csv_df[cn2] = ds.median(numeric_only=True)
        elif w_func == "count":
            csv_df[cn2] = ds.count(numeric_only=True)
        elif w_func == "skew":
            csv_df[cn2] = ds.skew(numeric_only=True)
        elif w_func == "kurt":
            csv_df[cn2] = ds.kurt(axis=0, skipna=True, numeric_only=True)
        elif w_func == "corr":
            csv_df[cn2] = ds.corr()
        elif w_func == "kurt":
            csv_df[cn2] = ds.cov()

        print("%inf:csv_window_rolling:new column {} was added".format(cn2), file=sys.stderr)

    csv_df.to_csv(output_file)
