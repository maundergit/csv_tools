#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_meltpivot.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-11-04 18:19:05>
# Licence:
#  Copyright (c) 2021 Masaharu N. Akei
#
#  This software is released under the MIT License.
#    http://opensource.org/licenses/mit-license.php
# ----------------------------------------------------------------------
import argparse
import textwrap
import sys

from distutils.version import LooseVersion

import re
import numpy as np
import pandas as pd

VERSION = 1.0

PANDAS_MIN_VERSION = "1.1.3"
if LooseVersion(PANDAS_MIN_VERSION) > LooseVersion(pd.__version__):
    print("??Error:csv_uty:padnas version must be newer than {}.".format(PANDAS_MIN_VERSION), file=sys.stderr)
    sys.exit(1)


def init():
    arg_parser = argparse.ArgumentParser(description="melting or pivoting csv file",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:
  The columns, that are given by '--values', must have data type of numeric.

  For mode==melt, when 'columns' argument is not given, others than 'key_columns' are used as 'columns'.

  For mode=pivot, np.sum is used as aggregator function.
  'columns' must be given. NaNs in results are filled by 0.
  If without '--values', it is done with assuming all 'values'=1(pandas.get_dummies() si used)
  For '--single_index_columns', the name of first column, that are given as 'columns', is used 
  to make multiindex of columns into a single index for columns.

example:
  csv_meltpivot.py --category_name=Category --value_name=Value bit-pattern-headers.csv ABC002 BIT000,BIT001,BIT003,BIT004 | head
| ABC002              | Category | Value |
| ------------------- | -------- | ----- |
| 2020-12-01 10:10:15 | BIT000   | 0     |
| 2020-12-01 10:10:17 | BIT000   | 1     |
| 2020-12-01 10:10:19 | BIT000   | 0     |
| 2020-12-01 10:10:21 | BIT000   | 0     |
| 2020-12-01 10:10:23 | BIT000   | 0     |
| 2020-12-01 10:10:25 | BIT000   | 1     |
| 2020-12-01 10:10:27 | BIT000   | 0     |
| 2020-12-01 10:10:29 | BIT000   | 0     |

# in 'test.csv' , above results were stored.
  csv_meltpivot.py --mode pivot --value=Value --single_index_columns test.csv ABC002 Category | csvlook -I
| ABC002              | BIT000 | BIT001 | BIT003 | BIT004 |
| ------------------- | ------ | ------ | ------ | ------ |
| 2020-12-01 10:10:15 | 0      | 1      | 0      | 0      |
| 2020-12-01 10:10:17 | 1      | 0      | 1      | 0      |
| 2020-12-01 10:10:19 | 0      | 0      | 0      | 0      |
| 2020-12-01 10:10:21 | 0      | 0      | 1      | 1      |
| 2020-12-01 10:10:23 | 0      | 1      | 0      | 1      |
| 2020-12-01 10:10:25 | 1      | 0      | 0      | 0      |
| 2020-12-01 10:10:27 | 0      | 1      | 0      | 0      |
| 2020-12-01 10:10:29 | 0      | 1      | 1      | 0      |
| 2020-12-01 10:10:31 | 1      | 1      | 1      | 1      |

  csv_meltpivot.py --mode pivot --values=COL003 test_melt_pivot.csv COL001 COL002 | csvlook -I
| COL001 | CAT0 | CAT1 | CAT2 |
| ------ | ---- | ---- | ---- |
| A      | 1    | 0    | 0    |
| B      | 0    | 0    | 0    |
| C      | 0    | 0    | 2    |

 csv_meltpivot.py --mode pivot --values=COL003 --single_index_columns test_melt_pivot.csv COL001 COL002 | csv_meltpivot.py - COL001| csvlook -I
| COL001 | Category | Value |
| ------ | -------- | ----- |
| A      | CAT1     | 0     |
| B      | CAT1     | 0     |
| C      | CAT1     | 0     |
| A      | CAT0     | 1     |
| B      | CAT0     | 0     |
| C      | CAT0     | 0     |
| A      | CAT2     | 0     |
| B      | CAT2     | 0     |
| C      | CAT2     | 2     |

  csv_meltpivot.py --mode pivot test_melt_pivot.csv COL001 COL002|csvlook -I
%Inf:csv_meltpivot: pivoting without values
| COL001 | COL003 | CAT0 | CAT1 | CAT2 |
| ------ | ------ | ---- | ---- | ---- |
| A      | 1      | 1    | 0    | 0    |
| B      | 0      | 0    | 1    | 0    |
| C      | 2      | 0    | 0    | 1    |

  csv_meltpivot.py --mode pivot test_melt_pivot.csv COL001 COL002,COL003|csvlook -I
%Inf:csv_meltpivot: pivoting without values
| COL001 | COL002_CAT0 | COL002_CAT1 | COL002_CAT2 | COL003_0 | COL003_1 | COL003_2 |
| ------ | ----------- | ----------- | ----------- | -------- | -------- | -------- |
| A      | 1           | 0           | 0           | 0        | 1        | 0        |
| B      | 0           | 1           | 0           | 1        | 0        | 0        |
| C      | 0           | 0           | 1           | 0        | 0        | 1        |

# in above example, this data was used.
 cat test_melt_pivot.csv|csvlook -I
| COL001 | COL002 | COL003 |
| ------ | ------ | ------ |
| A      | CAT0   | 1      |
| B      | CAT1   | 0      |
| C      | CAT2   | 2      |


'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))

    arg_parser.add_argument("--mode", dest="MODE", help="mode, default=melt", choices=["melt", "pivot"], default="melt")

    arg_parser.add_argument("--category_name",
                            dest="CNAME",
                            help="name of column that is stored names of columns",
                            type=str,
                            metavar='NAME',
                            default="Category")
    arg_parser.add_argument("--value_name",
                            dest="VNAME",
                            help="name of column that is stored value of each column",
                            type=str,
                            metavar='NAME',
                            default="Value")
    arg_parser.add_argument("--values",
                            dest="VCOLUMNS",
                            help="value columns for pivot mode",
                            type=str,
                            metavar='COLUMN[,COLUMN...]',
                            default=None)

    arg_parser.add_argument("--single_index_columns",
                            dest="SINGLE_INDEX",
                            help="single index for columns for pivot mode",
                            action="store_true",
                            default=False)

    arg_parser.add_argument("--output", dest="OUTPUT", help="path of output file", type=str, metavar='FILE', default=sys.stdout)

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='files to read, if empty, stdin is used', default=None)
    arg_parser.add_argument('key_columns',
                            metavar="KEY_COLUMN[,KEY_COLUMN...]",
                            help="names of key columns(index columns)",
                            type=str,
                            default=None)
    arg_parser.add_argument('columns', nargs='?', metavar="COLUM[,COLUMN...]", help="names of value columns", type=str, default=None)
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    args = init()
    csv_file = args.csv_file
    output_file = args.OUTPUT

    mode = args.MODE
    key_columns_s = args.key_columns
    columns_s = args.columns
    value_columns_s = args.VCOLUMNS
    column_name = args.CNAME
    value_name = args.VNAME
    single_index = args.SINGLE_INDEX

    if csv_file == "-":
        in_file = sys.stdin
    else:
        in_file = csv_file

    key_columns = []
    if key_columns_s is not None:
        key_columns = re.split(r"\s*,\s*", key_columns_s)

    columns = []
    if columns_s is not None:
        columns = re.split(r"\s*,\s*", columns_s)

    value_columns = []
    if value_columns_s is not None:
        value_columns = re.split(r"\s*,\s*", value_columns_s)

    if mode == "pivot":
        if len(columns) == 0:
            print("??error:csv_meltpivot: columns argument is reuired for mode=pivot", file=sys.stderr)
            sys.exit(1)
        if len(value_columns) == 0:
            print("%Inf:csv_meltpivot: pivoting without values", file=sys.stderr)

    csv_df = pd.read_csv(in_file)

    params = {}
    if mode == "melt":
        params.update({'ignore_index': True})
        if column_name is not None:
            params.update({"var_name": column_name})
        if value_name is not None:
            params.update({"value_name": value_name})
        if len(columns) == 0:
            columns = list(set(csv_df.columns) - set(key_columns))
        output_df = pd.melt(csv_df, id_vars=key_columns, value_vars=columns, **params)
        # print(output_df.loc[output_df[value_name] > 0])
        csv_index = False
    elif mode == "pivot":
        params.update({'values': value_columns})
        if len(value_columns) == 0:
            if len(columns) == 1:
                dm_prefix = ""
                dm_sep = ""
            else:
                dm_prefix = None
                dm_sep = "_"
            output_df = pd.get_dummies(csv_df, columns=columns, dummy_na=False, prefix=dm_prefix, prefix_sep=dm_sep)
            csv_index = False
        else:
            output_df = pd.pivot_table(csv_df, index=key_columns, columns=columns, **params, aggfunc=np.sum, fill_value=0)
            csv_index = True
        # output_df = csv_df.pivot(index=key_columns, columns=columns, **params)
        if single_index:
            cname = columns[0]
            output_df.columns = output_df.columns.get_level_values(cname)
            # output_df.columns = [v[1] for v in output_df.columns]

    output_df.to_csv(output_file, index=csv_index)
