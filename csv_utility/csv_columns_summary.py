#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_columns_summary.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-10-23 18:42:11>
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
import numpy as np
import pandas as pd

VERSION = 1.0

STATUS_FUNCTIONS = ['all', 'count', 'sum', 'avg', 'min', 'max', 'std', 'median']


def init():
    arg_parser = argparse.ArgumentParser(description="statistics summary for each colunm with CSV format",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
example:
  csv_columns_summary.py --function=sum --columns=A,B test1.csv
  csv_columns_summary.py --count=1 test1.csv
  csv_columns_summary.py --function=all --columns=A,B test1.csv| csvlook -I
| columns | count | sum | avg                | min | max | std                | median |
| ------- | ----- | --- | ------------------ | --- | --- | ------------------ | ------ |
| A       | 2.0   | 5.0 | 1.6666666666666667 | 0.0 | 4.0 | 2.0816659994661326 | 1.0    |
| B       | 2.0   | 7.0 | 2.3333333333333335 | 0.0 | 5.0 | 2.5166114784235836 | 2.0    |
'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    # arg_parser.add_argument("--something_3", dest="SOME_3", help="something", action="store_true", default=False)

    arg_parser.add_argument("--columns",
                            dest="COLUMNS",
                            help="columns to do function, default=all columns that have numeric values",
                            type=str,
                            metavar='COLUMN[,COLUMN...]',
                            default=None)
    arg_parser.add_argument("--function", dest="FUNC", choices=STATUS_FUNCTIONS, help="function to do", type=str, default="all")
    arg_parser.add_argument("--count",
                            dest="COUNTS",
                            help="count of given value. if given, '--function' is ignored.",
                            type=str,
                            metavar="STRING",
                            default=None)

    arg_parser.add_argument("--output", dest="OUTPUT", help="path of output file, default=stdout", type=str, metavar='FILE', default=None)

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='files to read, if empty, stdin is used')
    args = arg_parser.parse_args()
    return args


def count_in_series(ds, string_for_count):
    if format(ds.dtype) == 'object' or format(ds.dtype) == 'string'):
        result = ds[ds == count_s].count()
    elif np.dtype('float64') == ds.dtype or np.dtype('int64') == ds.dtype:
        try:
            result = ds[ds == float(count_s)].count()
        except ValueError:
            result = 0
    else:
        print("#warn:csv_columns_summary:column:{} has unknown data type:{}".format(ds.name, ds.dtype), file=sys.stderr)
        result = 0
    return result


if __name__ == "__main__":
    args = init()
    csv_file = args.csv_file
    columns_s = args.COLUMNS
    f_mode = args.FUNC
    output_file = args.OUTPUT
    count_s = args.COUNTS

    if csv_file == "-":
        csv_file = sys.stdin

    if output_file is None:
        output_file = sys.stdout

    csv_df = pd.read_csv(csv_file)
    if columns_s is not None:
        columns = re.split(r"\s*,\s*", columns_s)
    else:
        columns = list(csv_df.columns)

    if f_mode == "all":
        h_names = STATUS_FUNCTIONS[1:]
    else:
        h_names = [f_mode]
    if count_s is not None:
        h_names = ["count_string_{}".format(count_s)]

    out_df = pd.DataFrame(columns=h_names)
    out_df.index.name = "columns"
    for cname in columns:
        if cname not in csv_df.columns:
            print("#warn:csv_columns_summary:{} dose not exists".format(cname), file=sys.stderr)
            continue
        vals = []
        if count_s is not None:
            ds = csv_df[cname]
            vals.append(count_in_series(ds, count_s))
        elif np.dtype('float64') == csv_df[cname].dtype or np.dtype('int64') == csv_df[cname].dtype:
            if f_mode == "all":
                vals.extend([
                    len(csv_df.loc[csv_df[cname] != 0].dropna()), csv_df[cname].sum(), csv_df[cname].mean(), csv_df[cname].min(),
                    csv_df[cname].max(), csv_df[cname].std(), csv_df[cname].median()
                ])
            elif f_mode == "count":
                vals.append(len(csv_df.loc[csv_df[cname] != 0].dropna()))
            elif f_mode == "sum":
                vals.append(csv_df[cname].sum())
            elif f_mode == "avg":
                vals.append(csv_df[cname].mean())
            elif f_mode == "min":
                vals.append(csv_df[cname].min())
            elif f_mode == "max":
                vals.append(csv_df[cname].max())
            elif f_mode == "std":
                vals.append(csv_df[cname].std())
            elif f_mode == "median":
                vals.append(csv_df[cname].median())
        elif count_s is None:
            print("#warn:csv_columns_summary:skipped:data type of '{}' is {}.".format(cname, csv_df[cname].dtype), file=sys.stderr)
            continue
        out_df.loc[cname] = vals

    if len(out_df) > 0:
        out_df.to_csv(output_file)
    else:
        print("??Error:csv_columns_summary:result is empty ", file=sys.stderr)
