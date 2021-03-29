#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_status.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-08-16 12:33:46>
# Licence:
#  Copyright (c) 2021 Masaharu N. Akei
#
#  This software is released under the MIT License.
#    http://opensource.org/licenses/mit-license.php
# ----------------------------------------------------------------------
import argparse
import textwrap
import sys
# import pprint

import pandas as pd
from distutils.version import LooseVersion

PANDAS_MIN_VERSION = "1.1.3"
if LooseVersion(PANDAS_MIN_VERSION) > LooseVersion(pd.__version__):
    print("??Error:csv_uty:padnas version must be newer than {}.".format(PANDAS_MIN_VERSION), file=sys.stderr)
    sys.exit(1)

VERSION = 1.0

MODE_TABLE_DESC = {
    "count": "Count non-NA cells for each column",
    "sum": "Return the sum of the values for index",
    "avg": "Return the mean of index",
    "std": "Return sample standard deviation over index",
    "min": "Return the minimum of the values for index",
    "max": "Return the maximum of the values for index",
    "mode": "without '--group': Get the mode(s) of each element along index",
    "median": "Return the median of the values for index",
    "rank": "Compute numerical data ranks (1 through n) along index",
    "sem": "Return unbiased standard error of the mean over index",
    "skew": "Return unbiased skew over index",
    "var": "Return unbiased variance over index",
    "mad": "without '--group':Return the mean absolute deviation of the values for index",
    "kurt": "without '--group': Return unbiased kurtosis over index",
    "quantile25": "Return values at the given quantile over(=25%)",
    "quantile50": "Return values at the given quantile over(=50%)=median",
    "quantile75": "Return values at the given quantile over(=75%)",
    "nunique": "Count distinct observations over index",
    "cumsum": "Return cumulative sum over index",
    "cumprod": "Return cumulative product over index",
    "vrange": "Return range of value(max-min)",
    "notzero": "Count not zero elements over index",
    "zero": "Count zero elements over index",
    "morethan": "Coount elements over index, that have more than given value",
    "lessthan": "Coount elements over index, that have less than given value",
    "positive": "Coount elements over index, that have more than 0",
    "negative": "Coount elements over index, that have less than 0",
}
MODE_TABLE = list(MODE_TABLE_DESC.keys())


def init():

    mode_help = ""
    for k, v in MODE_TABLE_DESC.items():
        mode_help += "    {:6s}:{}\n".format(k, v)

    arg_parser = argparse.ArgumentParser(description="to derive statitical information for each columns",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:
  For '--mode', there are results for only columns that have numerical values.
  For '--mode mode', there is result that has 2D data, and if items that have the same count, there are more rows than one in result.

  With '--group', each histogram is made of value grouped by given group column.  

  description of mode:
{}

example:
  csv_status.py --mode morethan --arguments=3740 bit-pattern-headers.csv
  csv_uty.py --change_timefreq='D=ABC002:%Y-%m-%d %H\:%M\:%S:floor:10s' bit-pattern-headers.csv|\\
     csv_status.py --mode sum --group D -|csv_uty.py --drop_columns=ABC000,ABC001 - |\\
     csv_trimtime.py --stack=D - |csv_plot_bar.py --output=test.html --animation_column=D - category stacked_result

  csv_status.py --columns=2,5 big_sample_headers.csv
  == information for columns: ABC001
  count    1116.000000
  mean     4461.000000
  std      2578.446044
  min         1.000000
  25%      2231.000000
  50%      4461.000000
  75%      6691.000000
  max      8921.000000
  Name: ABC001, dtype: float64

  == information for columns: ABC004
  count      1116
  unique        2
  top       A0001
  freq        897
  Name: ABC004, dtype: object
  unique values:
  ('A0001', 897)
  ('B0010', 219)

'''.format(mode_help)))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument("--columns",
                            dest="COLUMNS",
                            help="name or index of columns as csv format",
                            type=str,
                            metavar='COLUMNS',
                            default=None)

    arg_parser.add_argument("--mode", dest="MODE", help="name of columns to make group", choices=MODE_TABLE, default=None)
    arg_parser.add_argument("--group", dest="GCOLUMN", help="name of columns to make group", type=str, metavar='COLUMN', default=None)
    arg_parser.add_argument("--arguments", dest="OPTARGS", help="arguments for some mode", type=str, metavar="ARG[,ARG...]", default=None)

    arg_parser.add_argument("--output",
                            dest="OUTPUT",
                            help="path of output csv file, default=stdout",
                            type=str,
                            metavar='FILE',
                            default=sys.stdout)

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='files to read, if empty, stdin is used')
    args = arg_parser.parse_args()
    return args


def series_statistics(ps):
    """print statistics about pandas.Series

    :param ps: panas.Series 

    """
    if ps.dtype == object:
        print(ps.describe(include='all'))
        print("-- unique values:")
        vcs = list(ps.value_counts().items())
        if len(vcs) > 10:
            print("#Warning:csv_status:too many uniqe values:{}".format(ps.nunique()), file=sys.stderr)
            max_print = 10
            print("\n".join([str(v) for v in vcs[:max_print]]))
            if len(vcs) - max_print > max_print:
                print(":\n:")
                print("\n".join([str(v) for v in vcs[-max_print:]]))
            else:
                print(vcs[max_print:])
        else:
            print("\n".join([str(v) for v in vcs]))

    else:
        print(ps.describe(include='all'))
        idxmax = ps.idxmax()
        idxmin = ps.idxmin()
        print("maximum value: pos={}, value={}".format(idxmax, ps.iloc[idxmax]))
        print("minimum value: pos={}, value={}".format(idxmin, ps.iloc[idxmin]))

    print("NA count: {}".format(ps.isnull().sum()))
    print("")


def entire_status(csv_df, output, col_list):
    # for each columns
    if len(col_list) > 0:
        cnames = csv_df.columns
        for cn in col_list:
            if cn not in cnames:
                print("#warn:csv_status:column:{} not found".format(cn), file=sys.stderr)
            else:
                c_ps = csv_df[cn]
                print("== information for columns:{} of {}".format(cn, csv_file), file=output)
                print("dtype   {}".format(c_ps.dtype), file=output)
                series_statistics(c_ps)

    else:
        cnames = csv_df.columns
        pd.set_option('display.max_rows', 500)
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1000)
        print("==== csv file: {}".format(csv_file), file=output)
        print("-- number of rows   : {}".format(len(csv_df)), file=output)
        print("-- number of columsn: {}".format(len(cnames)), file=output)
        print("-- duplicated rows  : {}".format(len(csv_df[csv_df.duplicated()])), file=output)
        print("-- statistical information for each column", file=output)
        print(csv_df.describe(include='all'), file=output)
        print("-- NA count", file=output)
        print(csv_df.isnull().sum(), file=output)


def status_by_mode(df, output, mode, group_col, opt_args):

    if group_col is not None:
        w_df = df.groupby(group_col)
    else:
        w_df = df

    if mode == "positive" or mode == "negative":
        opt_args = [0]

    if mode == "count":
        r_df = w_df.count()
    elif mode == "sum":
        r_df = w_df.sum(numeric_only=True)
    elif mode == "avg":
        r_df = w_df.mean(numeric_only=True)
    elif mode == "std":
        r_df = w_df.std()
    elif mode == "min":
        r_df = w_df.min(numeric_only=True)
    elif mode == "max":
        r_df = w_df.max(numeric_only=True)
    elif group_col is None and mode == "mode":
        r_df = w_df.mode(numeric_only=True)
    elif mode == "median":
        r_df = w_df.median(numeric_only=True)
    elif mode == "rank":
        r_df = w_df.rank()
    elif mode == "sem":
        r_df = w_df.sem()
    elif mode == "skew":
        r_df = w_df.skew(numeric_only=True)
    elif mode == "var":
        r_df = w_df.var()
    elif group_col is None and mode == "mad":
        r_df = w_df.mad(axis=0, skipna=True)
    elif group_col is None and mode == "kurt":
        r_df = w_df.kurt(axis=0, skipna=True, numeric_only=True)
    elif mode == "quantile25":
        r_df = w_df.quantile(q=0.25)
    elif mode == "quantile50":
        r_df = w_df.quantile(q=0.50)
    elif mode == "quantile75":
        r_df = w_df.quantile(q=0.75)
    elif mode == "nunique":
        r_df = w_df.nunique()
    elif mode == "cumsum":
        r_df = w_df.cumsum(axis=0, skipna=True)
    elif mode == "cumprod":
        r_df = w_df.cumsum(axis=0, skipna=True)
    elif mode == "vrange":
        r_df = w_df.max(numeric_only=True) - w_df.min(numeric_only=True)
    elif mode == "notzero":
        w_df = w_df.select_dtypes(include=['int16', 'int32', 'int64', 'float16', 'float32', 'float64'])
        # w_df = w_df.where(w_df == 0, 1)
        w_df = w_df.mask(w_df > 0, 1)
        r_df = w_df.sum()
    elif mode == "zero":
        w_df = w_df.select_dtypes(include=['int16', 'int32', 'int64', 'float16', 'float32', 'float64'])
        # w_df = w_df.where(w_df == 0, 1)
        w_df = w_df.mask(w_df > 0, 1).apply(lambda x: 1 - x)
        r_df = w_df.sum()
    elif mode == "morethan" or mode == "positive":
        if len(opt_args) == 0:
            print("??error:csv_status:for {}, '--arguments' is required.".format(mode), file=sys.stderr)
            sys.exit(1)
        w_df = w_df.select_dtypes(include=['int16', 'int32', 'int64', 'float16', 'float32', 'float64'])
        print("%inf:csv_status:if mode={}, only columns that have numeric values were selected:{}".format(mode, list(w_df.columns)),
              file=sys.stderr)
        # w_df = w_df.where(w_df == 0, 1)
        v_limit = float(opt_args[0])
        w_df = w_df.mask(w_df <= v_limit, 0)
        w_df = w_df.mask(w_df > v_limit, 1)
        r_df = w_df.sum()
    elif mode == "lessthan" or mode == "negative":
        if len(opt_args) == 0:
            print("??error:csv_status:for {}, '--arguments' is required.".format(mode), file=sys.stderr)
            sys.exit(1)
        w_df = w_df.select_dtypes(include=['int16', 'int32', 'int64', 'float16', 'float32', 'float64'])
        print("%inf:csv_status:if mode={}, only columns that have numeric values were selected:{}".format(mode, list(w_df.columns)),
              file=sys.stderr)
        # w_df = w_df.where(w_df == 0, 1)
        v_limit = float(opt_args[0])
        w_df = w_df.mask(w_df < v_limit, 1)
        w_df = w_df.mask(w_df >= v_limit, 0)
        r_df = w_df.sum()
    else:
        print("??erro:csv_status:invalid mode:{}".format(mode), file=sys.stderr)
        sys.exit(1)

    if group_col is None:
        r_df.index.name = "column"
        r_df.name = mode
    r_df.to_csv(output)


if __name__ == "__main__":
    import re
    args = init()
    csv_file = args.csv_file
    output_file = args.OUTPUT
    col_list_a = args.COLUMNS
    group_column = args.GCOLUMN
    mode = args.MODE
    opt_args_s = args.OPTARGS

    if csv_file == "-":
        csv_file = sys.stdin
    if output_file is None:
        output_file = sys.stdout
    elif isinstance(output_file, str):
        output_file = open(output_file, "w")

    opt_args = []
    if opt_args_s is not None:
        opt_args = re.split(r"(?<!\\)\s*,\s*", opt_args_s)

    csv_df = pd.read_csv(csv_file)

    if col_list_a is not None:
        cnames = csv_df.columns
        col_list = re.split(r"\s*,\s*", col_list_a)
        if any([re.match(r'^\d+$', v) is not None and int(v) <= 0 for v in col_list]):
            print("??Error:csv_status:column index must be positive integer", file=sys.stderr)
            sys.exit(1)
        if any([re.match(r'^\d+$', v) is not None and int(v) > len(cnames) for v in col_list]):
            print("??Error:csv_status:given column index more than one in the file: {}".format(len(cnames)), file=sys.stderr)
            sys.exit(1)
        col_list = [cnames[int(v) - 1] if re.match(r'^\d+$', v) is not None else v for v in col_list]
    else:
        col_list = []

    rest_cols = set(col_list) - set(csv_df.columns)
    if len(rest_cols) > 0:
        print("??error:csv_status:invalid columns:{}".format(rest_cols), file=sys.stderr)
        sys.exit(1)

    if mode is None:
        entire_status(csv_df, output_file, col_list)
    else:
        print("%inf:csv_status:mode={},group={}".format(mode, group_column), file=sys.stderr)
        if len(col_list) > 0:
            csv_df = csv_df[col_list]
        status_by_mode(csv_df, output_file, mode, group_column, opt_args)
