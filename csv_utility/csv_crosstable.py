#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_crosstable.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-11-07 08:18:04>
# Licence:
#  Copyright (c) 2021 Masaharu N. Akei
#
#  This software is released under the MIT License.
#    http://opensource.org/licenses/mit-license.php
# ----------------------------------------------------------------------
import argparse
import fileinput
import textwrap
import sys

from pathlib import Path

import re
import numpy as np
import pandas as pd

VERSION = 1.0

AGG_FUNCTIONS = ["sum", "min", "max", "mean", "median", "prod", "count_nonzero"]


def init():
    arg_parser = argparse.ArgumentParser(description="make cross-matching table from csv file",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:

  For '--normalize', following are available.
   ‘all’     : normalize over all values.
   ‘index’   : normalize over each row.
   ‘columns’ : normalize over each column.
  see 'pandas.crosstab https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.crosstab.html'

example:

# input data for example
cat test_crosstable.csv|csvlook -I
| COL001 | COL002 | COL003 | COL004 | COL005 |
| ------ | ------ | ------ | ------ | ------ |
| A      | a      | 1      | 2      | Z      |
| B      | b      | 1      | 3      | X      |
| C      | c      | 1      | 4      | Y      |
| D      | d      | 1      | 5      | Z      |
| A      | b      | 1      | 6      | V      |
| B      | c      | 1      | 7      | W      |
| C      | d      | 1      | 8      | S      |
| D      | a      | 1      | 9      | T      |

csv_crosstable.py test_crosstable.csv COL001 COL002|csvlook -I
| COL001 | a | b | c | d |
| ------ | - | - | - | - |
| A      | 1 | 1 | 0 | 0 |
| B      | 0 | 1 | 1 | 0 |
| C      | 0 | 0 | 1 | 1 |
| D      | 1 | 0 | 0 | 1 |

csv_crosstable.py test_crosstable.csv --values=COL004 COL001 COL002|csvlook -I
| COL001 | a   | b   | c   | d   |
| ------ | --- | --- | --- | --- |
| A      | 2.0 | 6.0 |     |     |
| B      |     | 3.0 | 7.0 |     |
| C      |     |     | 4.0 | 8.0 |
| D      | 9.0 |     |     | 5.0 |

csv_crosstable.py test_crosstable.csv --values=COL004 --aggregator=prod COL001 COL002,COL005
COL002,a,a,a,a,a,a,a,b,b,b,b,b,b,b,c,c,c,c,c,c,c,d,d,d,d,d,d,d
COL005,S,T,V,W,X,Y,Z,S,T,V,W,X,Y,Z,S,T,V,W,X,Y,Z,S,T,V,W,X,Y,Z
COL001,,,,,,,,,,,,,,,,,,,,,,,,,,,,
A,,,,,,,2.0,,,6.0,,,,,,,,,,,,,,,,,,
B,,,,,,,,,,,,3.0,,,,,,7.0,,,,,,,,,,
C,,,,,,,,,,,,,,,,,,,,4.0,,8.0,,,,,,
D,,9.0,,,,,,,,,,,,,,,,,,,,,,,,,,5.0

# with '--suppress_all_zero'
csv_crosstable.py test_crosstable.csv --values=COL004 --aggregator=prod --suppress_all_zero COL001 COL002,COL005
COL002,a,a,b,b,c,c,d,d
COL005,T,Z,V,X,W,Y,S,Z
COL001,,,,,,,,
A,,2.0,6.0,,,,,
B,,,,3.0,7.0,,,
C,,,,,,4.0,8.0,
D,9.0,,,,,,,5.0

'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument("--values", dest="VCOLUMN", help="name of column for value", type=str, metavar='COLUMN', default=None)
    arg_parser.add_argument("--aggregator",
                            dest="AFUNC",
                            help="aggregator function for '--values', default='sum'",
                            choices=AGG_FUNCTIONS,
                            default="sum")
    arg_parser.add_argument("--row_names",
                            dest="RNAMES",
                            help="names of rows in output,default=names of given rows",
                            type=str,
                            metavar='NAME[,NAME...]',
                            default=None)
    arg_parser.add_argument("--column_names",
                            dest="CNAMES",
                            help="names of columns in output,default=names of given columns",
                            type=str,
                            metavar='NAME[,NAME...]',
                            default=None)
    arg_parser.add_argument("--normalize",
                            dest="NORM",
                            help="normalized mode, see 'remark'",
                            choices=["all", "index", "column"],
                            default=False)
    arg_parser.add_argument("--suppress_all_zero",
                            dest="SAZ",
                            help="suppress outputing columns whose elements are all NaN",
                            action='store_true')

    arg_parser.add_argument("--output_file",
                            dest="OUTPUT",
                            help="path of output file,default=stdout",
                            type=str,
                            metavar="FILE",
                            default=sys.stdout)

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='files to read, if empty, stdin is used')
    arg_parser.add_argument('rows', metavar="ROW_COLUMN[,ROW_COLUMN...]", type=str)
    arg_parser.add_argument('columns', metavar="COLUMN[,COLUMN...]", type=str)
    # arg_parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    args = init()
    csv_file = args.csv_file
    rownames_s = args.rows
    rownames = re.split(r"\s*,\s*", rownames_s)
    colnames_s = args.columns
    colnames = re.split(r"\s*,\s*", colnames_s)

    if csv_file == "-":
        csv_file = sys.stdin
    output_file = args.OUTPUT

    ct_params = {"dropna": args.SAZ}
    norms = args.NORM
    ct_params.update({"normalize": norms})

    rnames_s = args.RNAMES
    if rnames_s is not None:
        rnames = re.split(r"\s*,\s*", rnames_s)
        if len(rnames) != len(rownames):
            print("??Error:csv_crosstable:number of columns given by '--row_names' must be equlat to number of rows", file=sys.stderr)
            sys.exit(1)
        ct_params.update({"rownames": rnames})
    cnames_s = args.CNAMES
    if cnames_s is not None:
        cnames = re.split(r"\s*,\s*", cnames_s)
        if len(cnames) != len(colnames):
            print("??Error:csv_crosstable:number of columns given by '--column_names' must be equlat to number of columns",
                  file=sys.stderr)
            sys.exit(1)
        ct_params.update({"colnames": cnames})

    values = args.VCOLUMN
    aggfunc_s = args.AFUNC
    if aggfunc_s == "sum":
        aggfunc = np.sum
    elif aggfunc_s == "mean":
        aggfunc = np.mean
    elif aggfunc_s == "max":
        aggfunc = np.max
    elif aggfunc_s == "min":
        aggfunc = np.min
    elif aggfunc_s == "median":
        aggfunc = np.median
    elif aggfunc_s == "prod":
        aggfunc = np.median
    elif aggfunc_s == "count_nonzero":
        aggfunc = np.count_nonzero

    csv_df = pd.read_csv(csv_file)
    if values is not None:
        ct_params.update({"values": csv_df[values], "aggfunc": aggfunc})

    idxs = []
    for rn in rownames:
        idxs.append(csv_df[rn])
    cols = []
    for cn in colnames:
        cols.append(csv_df[cn])
    output_df = pd.crosstab(idxs, cols, **ct_params)

    # print(output_df)
    output_df.to_csv(output_file)
