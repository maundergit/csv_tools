#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_trimtime.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-11-13 08:49:20>
# Licence:
#  Copyright (c) 2021 Masaharu N. Akei
#
#  This software is released under the MIT License.
#    http://opensource.org/licenses/mit-license.php
# ----------------------------------------------------------------------
import argparse
import textwrap
import sys

from datetime import timedelta
from datetime import datetime as dtt

import re
import numpy as np
import pandas as pd

VERSION = 1.0

RESAMPLE_METHOD_INTERPOLATE = [
    "linear", "quadratic", "cubic", "spline", "barycentric", "polynomial", "krogh", "piecewise_polynomial", "pchip", "akima",
    "cubicspline"
]

RESAMPLE_METHOD = ["nearest", "count", "sum", "min", "max", "mean", "std"] + RESAMPLE_METHOD_INTERPOLATE


def init():
    arg_parser = argparse.ArgumentParser(description="triming columns that have time data",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''

remark:
  # Time series analysis with pandas https://ourcodingclub.github.io/tutorials/pandas-time-series/

  When '--get_range_of_time' was given, only range of time is printed to stdout without other processings.
  Available 'unit' to print is one of 'H'our, 'M'inuts, 'S'econds. See example.

  For '--change_timefreq', available methods are floor, ceil,round. About format string, you may find answer in folowing:
  'datetime  Basic date and time types https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior'.
  About 'freqnecy', you may check the document in following:
  'Time series / date functionality https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases'.

  If you make group according to gap in seriesed values or datetime, '--gap' or '--time_gap' are available.
  This group is useful for plotting by 'csv_plot_*', printing status by 'csv_status'.
  For '--time_gap', about time format string , see above about '--change_timefreq'
  using '--gap', numeric others than date time data are treated.
  For '--gap' and '--time_gap', given gap should be positive.

  If you want to use commas and colon in expression of '--change_timefreq' and others, those must be escaped by back-slash. see examples.

  processing order:
    sort datetime, convert into timestamp, add time column, reformat, gap, time gap, time diff, change timrefreq, resample, 
    select datetime range, select hours range

example:


  csv_trimtime.py --get_range_of_time='A:M' test_trimtime.csv
%inf:csv_uty:get time of range:A:13106.0 mins
  csv_trimtime.py --get_range_of_time='A:M' test_trimtime.csv | sed -E 's/^.*:([0-9.]+) mins/\1/'
13106.0

  csv_trimtime.py --sort_datetime=date a10.csv

  csv_trimtime.py --timestamp="D:A" test_trimtime.csv
  csv_trimtime.py --add_time_column="D:2020-12-01 12\:12\:12:5s" test_trimtime.csv
  csv_trimtime.py --reformat="A:%Y-%m-%d %H\:%M\:%S:%Y/%m/%dT%H\:%M\:%S" test_trimtime.csv
  csv_trimtime.py --gap="GC=C:1" test_trimtime.csv

  csv_trimtime.py --time_gap="GA=A::61" test_trimtime.csv
%Inf:csv_trimtime:groupby time gap
%inf:csv_trimtime:groupby_time_gap:['GA=A::61']
%inf:csv_trimtime:groupby_time_gap:column=GA:number of groups=4:max count in each group=3
A,B,C,GA
2020-11-14 10:00:00,1,19,0
2020-11-13 10:00:00,1,19,1
2020-11-13 10:01:00,2,18,1
2020-11-13 10:02:00,3,7,1

  csv_trimtime.py --change_timefreq='D=ABC002:%Y-%m-%d %H\:%M\:%S\:floor\:30s' big_sample_headers.csv |\\
                                                              csv_plot_histogram.py --animation_column=D --output=test.html - ABC005

  # in following example, column 'D' will be created as column of timestamp, and by those dataframe will be made into group and stacked.
  # at plot, the timestamp column 'D' will be used as animation key frames.
  csv_trimtime.py --change_timefreq='D=ABC002:%Y-%m-%d %H\:%M\:%S:floor:10s' bit-pattern-headers.csv|\\
     csv_status.py --mode sum --group D -|csv_uty.py --drop_columns=ABC000,ABC001 - |\\
     csv_uty.py --stack=D - |csv_plot_bar.py --output=bit-pattern-headers_10sec_sum.html --animation_column=D --yrange=0,1 - category stacked_result

  csv_trimtime.py --resample="A:%Y-%m-%d %H\:%M\:%S:2min:B,C" --resample_func=mean test_trimtime.csv

  csv_trimtime.py --select_hours="A:10\:00\:00,11\:00\:00" test_trimtime.csv
  csv_trimtime.py --select_hours="A:10\:00\:00,1\:00\:00pm" test_trimtime.csv
  csv_trimtime.py --select_datetime="date:%Y-%m-%d:2007-01-01,2007-12-01" a10.csv

  csv_trimtime.py --calculate_time_diff="TD=A:%Y-%m-%d %H\:%M\:%S:1" test_trimtime.csv
A,B,C,TD
2020-11-14 10:00:00,1,19,
2020-11-13 10:00:00,1,19,-86400.0
2020-11-13 10:01:00,2,18,60.0

  csv_trimtime.py --calculate_elapsed_time="G=date:%Y-%m-%d:2007-08-01 00\:00\:00" a10.csv
date,value,G
2007-06-01,20.681002,-5270400.0
2007-07-01,21.834889999999998,-2678400.0
2007-08-01,23.93020353,0.0
2007-09-01,22.93035694,2678400.0
2007-10-01,23.26333992,5270400.0


'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument("--get_range_of_time",
                            dest="GRANGE",
                            help="range of time of column, available unit:H,M,S" +
                            " if you use comma or colon in expression, those must be escaped with back-slash",
                            type=str,
                            metavar='COLUMN[:datetime_format]:unit',
                            default=None)

    arg_parser.add_argument("--sort_datetime",
                            dest="TSORT",
                            help="sort datetime, format of definition=column_name[:datetime_format]." +
                            "default datetime_format='%%Y-%%m-%%d %%H:%%M:%%S'." +
                            " if you use comma or colon in expression, those must be escaped with back-slash",
                            type=str,
                            metavar="COLUMN_NAME:datetime_format",
                            default=None)
    arg_parser.add_argument("--timestamp",
                            dest="TSTAMP",
                            help="convert date time column(COLUMN_0) into timestamp(COLUMN_1)",
                            type=str,
                            metavar='COLUMN_1:COLUMN_0',
                            default=None)
    arg_parser.add_argument("--add_time_column",
                            dest="TIMECOLUMN",
                            help="add new column of time series",
                            type=str,
                            metavar='COLUMN:start:freq',
                            default=None)
    arg_parser.add_argument("--reformat",
                            dest="REFORMAT",
                            help="change format of datetime of column" +
                            " if you use comma or colon in expression, those must be escaped with back-slash",
                            type=str,
                            metavar='COLUMN:in_format[:out_format]',
                            default=None)
    arg_parser.add_argument("--gap",
                            dest="GAP",
                            help="group by value gap, format of definitoin is 'group_column_name=col_name:gap'." +
                            " if you use comma or colon in expression, those must be escaped with back-slash",
                            type=str,
                            metavar='COLUMN=definition[,COLUMN=definition...]',
                            default=None)
    arg_parser.add_argument("--time_gap",
                            dest="TGAP",
                            help="group by time gap[seconds],format of definitoin is 'group_column_name=col_name:datetime_format:gap'." +
                            "unit of 'gap' is second." +
                            " if you use comma or colon in expression, those must be escaped with back-slash",
                            type=str,
                            metavar='COLUMN=definition[,COLUMN=definition...]',
                            default=None)

    arg_parser.add_argument(
        "--calculate_time_diff",
        dest="TDIFF",
        help="calculate difference[seconds] of datetime column,format of definitoin is 'column_name=col_name[:datetime_format[:step]]'." +
        "format is datetime format, default='%%Y-%%m-%%d %%H:%%M:%%S'. 'step' is integer value, default=1." +
        " if you use comma or colon in expression, those must be escaped with back-slash",
        type=str,
        metavar='COLUMN:definition',
        default=None)

    arg_parser.add_argument(
        "--calculate_elapsed_time",
        dest="ETIME",
        help=
        "calculate elapsed time[seconds] of datetime column,format of definitoin is 'column_name=col_name[:datetime_format[:origin]]'." +
        "format is datetime format, default='%%Y-%%m-%%d %%H:%%M:%%S'. 'origin' is datetime which format is '%%Y-%%m-%%d %%H:%%M:%%S'." +
        "if 'origin' was omitted, value at first row will be used as origin." +
        " if you use comma or colon in expression, those must be escaped with back-slash",
        type=str,
        metavar='COLUMN:definition',
        default=None)

    arg_parser.add_argument(
        "--change_timefreq",
        dest="CHTFREQ",
        help="change datetime frequeny unit:format of definitoin is 'new_column_name=old_col_name:datetime_format:method:frequency'." +
        " if you use comma or colon in expression, those must be escaped with back-slash",
        type=str,
        metavar='COLUMN=definition[,COLUMN=definition...]',
        default=None)
    arg_parser.add_argument(
        "--resample",
        dest="RESAMPLE",
        help="aggregating values of column resampled by time frequency, using function is defined by '--resample_function'",
        type=str,
        metavar='COLUMN[:time_format]:freq:COLUMN_TO_RESAMPLE[,COLUMN...]',
        default=None)
    arg_parser.add_argument("--resample_function",
                            dest="RESAMPLE_FUNC",
                            help="aggregation function for '--resample', default=mean",
                            choices=RESAMPLE_METHOD,
                            default="mean")
    arg_parser.add_argument(
        "--select_hours",
        dest="TSELECT_HOURS",
        help="select hours range, ex: 14:00-18:00 for every days. 'start_time' and 'end_time' have the format:%%H:%%M,%%H:%%M:%%S",
        type=str,
        metavar='COLUMN[:time_format]:start_time,end_time',
        default=None)

    arg_parser.add_argument("--select_datetime",
                            dest="TSELECT",
                            help="select datetime range, 'start_time' and 'end_time' have the same format as target column",
                            type=str,
                            metavar='COLUMN[:time_format]:start_time,end_time',
                            default=None)

    arg_parser.add_argument("--output",
                            dest="OUTPUT",
                            help="path of output csv file, default=stdout",
                            type=str,
                            metavar='FILE',
                            default=sys.stdout)

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='files to read, if empty, stdin is used')

    args = arg_parser.parse_args()
    return args


def change_time_frequency(df, ch_definitions):
    """FIXME! briefly describe function

    :param df: 
    :param ch_definitions: [new_column_name=old_column:format:method:frequency,...]
    :returns: 
    :rtype: 

    """
    print("%inf:csv_trimtime:change_timefreq:{}".format(ch_definitions), file=sys.stderr)

    try:
        for cdf in ch_definitions:
            cvs = re.split(r"\s*(?<!\\)=\s*", cdf)
            cname = cvs[0]
            if len(cvs) < 2:
                print("??error:csv_trimtime:change_timefreq:invalid format of definition:{}".format(cdf), file=sys.stderr)
                sys.exit(1)
            cvs = re.split(r"\s*(?<!\\):\s*", cvs[1])
            if len(cvs) < 3:
                print("??error:csv_trimtime:change_timefreq:invalid format of definition:{}".format(cdf), file=sys.stderr)
                sys.exit(1)
            t_col = cvs[0]
            t_format = cvs[1]
            t_method = cvs[2]
            t_freq = cvs[3]
            if len(t_format) > 0:
                t_format = re.sub(r"\\:", ":", t_format)
                t_format = re.sub(r"\\=", "=", t_format)
            else:
                t_format = "%Y-%m-%d %H:%M:%S"
            df[cname] = pd.to_datetime(df[t_col], format=t_format)
            if t_method == "floor":
                df[cname] = df[cname].dt.floor(t_freq).dt.strftime(t_format)
            elif t_method == "ceil":
                df[cname] = df[cname].dt.ceil(t_freq).dt.strftime(t_format)
            elif t_method == "round":
                df[cname] = df[cname].dt.round(t_freq).dt.strftime(t_format)
            else:
                print("#warn:csv_trimtime:invalid method for '--change_timefreq':{} in {}".format(t_method, cdf), file=sys.stderr)
                continue
            vcs = df[cname].value_counts()
            print("%inf:csv_trimtime:change_timefreq:column={}:number of uniq periods={}:max count in each period={}".format(
                cname, len(vcs), max(vcs)),
                  file=sys.stderr)
    except ValueError as e:
        print("??error:csv_trimtime:change time frequency:{}:{}".format(t_col, e), file=sys.stderr)
        sys.exit(1)

    return df


def groupby_time_gap(df, time_gap_definitions):
    """FIXME! briefly describe function

    :param df: 
    :param time_gap_definitions: [new_column_name=old_column:format:gap,...]
    :returns: 
    :rtype: 

    """
    print("%inf:csv_trimtime:groupby_time_gap:{}".format(time_gap_definitions), file=sys.stderr)

    try:
        for cdf in time_gap_definitions:
            cvs = re.split(r"\s*(?<!\\)=\s*", cdf)
            cname = cvs[0]
            if len(cvs) < 2:
                print("??error:csv_trimtime:groupby_time_gap:invalid format of definition:{}".format(cdf), file=sys.stderr)
                sys.exit(1)
            cvs = re.split(r"\s*(?<!\\):\s*", cvs[1])
            if len(cvs) < 3:
                print("??error:csv_trimtime:groupby_time_gap:invalid format of definition:{}".format(cdf), file=sys.stderr)
                sys.exit(1)
            t_col = cvs[0]
            t_format = cvs[1]
            t_gap = float(cvs[2])
            if len(t_format) > 0:
                t_format = re.sub(r"\\:", ":", t_format)
                t_format = re.sub(r"\\=", "=", t_format)
            else:
                t_format = "%Y-%m-%d %H:%M:%S"
            df[t_col] = pd.to_datetime(df[t_col], format=t_format)

            df = groupby_gap(df, t_col, cname, timedelta(seconds=t_gap))

            vcs = df[cname].value_counts()
            print("%inf:csv_trimtime:groupby_time_gap:column={}:number of groups={}:max count in each group={}".format(
                cname, len(vcs), max(vcs)),
                  file=sys.stderr)
    except ValueError as e:
        print("??error:csv_trimtime:groupby time gap:{}:{}".format(t_col, e), file=sys.stderr)
        sys.exit(1)

    return df


def groupby_value_gap(df, gap_definitions):
    """FIXME! briefly describe function

    :param df: 
    :param gap_definitions: [new_column_name=old_column:gap,...]
    :returns: 
    :rtype: 

    """
    print("%inf:csv_trimtime:groupby_gap:{}".format(gap_definitions), file=sys.stderr)

    try:
        for cdf in gap_definitions:
            cvs = re.split(r"\s*(?<!\\)=\s*", cdf)
            cname = cvs[0]
            if len(cvs) < 2:
                print("??error:csv_trimtime:groupby_gap:invalid format of definition:{}".format(cdf), file=sys.stderr)
                sys.exit(1)
            cvs = re.split(r"\s*(?<!\\):\s*", cvs[1])
            if len(cvs) < 2:
                print("??error:csv_trimtime:groupby_gap:invalid format of definition:{}".format(cdf), file=sys.stderr)
                sys.exit(1)
            t_col = cvs[0]
            t_gap = float(cvs[1])

            df = groupby_gap(df, t_col, cname, t_gap)

            vcs = df[cname].value_counts()
            print("%inf:csv_trimtime:groupby_gap:column={}:number of groups={}:max count in each group={}".format(
                cname, len(vcs), max(vcs)),
                  file=sys.stderr)
    except ValueError as e:
        print("??error:csv_trimtime:groupby gap:{}:{}".format(t_col, e), file=sys.stderr)
        sys.exit(1)

    return df


def groupby_gap(df, column_name, group_column_name, gap):
    """FIXME! briefly describe function

    :param df: 
    :param column_name: 
    :param group_column_name: 
    :param gap: numerica value or datetime.timedelta()
    :returns: 
    :rtype: 

    """

    dt_s = pd.Series([False] * len(df), index=df.index, dtype="boolean")
    dt_s.loc[df[column_name].diff().abs() > gap] = True

    if df[column_name].diff().abs().loc[dt_s].dtype != np.timedelta64:
        gap_list = list(df[column_name].diff().loc[dt_s].apply(lambda x: x.total_seconds()))
    else:
        gap_list = list(df[column_name].diff().loc[dt_s])
    print("%inf:csv_trimtime:detected gap values:\n{}".format(gap_list), file=sys.stderr)

    g_count = len(dt_s.loc[dt_s])
    df.loc[dt_s, group_column_name] = list(range(1, g_count + 1))
    df[group_column_name].iat[0] = 0
    df[group_column_name].ffill(axis=0, inplace=True)
    # df[group_column_name].fillna(g_count + 1, inplace=True)
    df[group_column_name] = df[group_column_name].astype('int64')
    return df


def calculate_time_diff(df, time_diff):
    cvs = re.split(r"\s*(?<!\\)=\s*", time_diff)
    cname = cvs[0]
    if len(cvs) < 2:
        print("??error:csv_trimtime:calculate_time_diff:invalid format of definition:{}".format(time_diff), file=sys.stderr)
        sys.exit(1)
    cvs = re.split(r"\s*(?<!\\):\s*", cvs[1])
    t_col = cvs[0]
    if len(cvs) < 2:
        t_format = ""
    else:
        t_format = cvs[1]
    if len(cvs) < 3:
        t_step = 1
    else:
        t_step = int(cvs[2])
    if len(t_format) > 0:
        t_format = re.sub(r"\\:", ":", t_format)
        t_format = re.sub(r"\\=", "=", t_format)
    else:
        t_format = "%Y-%m-%d %H:%M:%S"

    df[t_col] = pd.to_datetime(df[t_col], format=t_format)
    df[cname] = df[t_col].diff(t_step).apply(lambda x: x.total_seconds())

    print("%inf:csv_trimtime:calculate_time_diff:min={},max={},mean={}".format(df[cname].min(), df[cname].max(), df[cname].mean()),
          file=sys.stderr)

    return df


def calculate_elapsed_time(df, elapsed_time_def):
    cvs = re.split(r"\s*(?<!\\)=\s*", elapsed_time_def)
    cname = cvs[0]
    if len(cvs) < 2:
        print("??error:csv_trimtime:calculate_elapsed_time:invalid format of definition:{}".format(elapsed_time_def), file=sys.stderr)
        sys.exit(1)
    cvs = re.split(r"\s*(?<!\\):\s*", cvs[1])
    t_col = cvs[0]
    if len(cvs) < 2:
        t_format = ""
    else:
        t_format = cvs[1]
    if len(cvs) < 3:
        t_org = 0
    else:
        t_org = cvs[2]
        t_org = re.sub(r"\\:", ":", t_org)
        t_org = dtt.strptime(t_org, "%Y-%m-%d %H:%M:%S")
    if len(t_format) > 0:
        t_format = re.sub(r"\\:", ":", t_format)
        t_format = re.sub(r"\\=", "=", t_format)
    else:
        t_format = "%Y-%m-%d %H:%M:%S"

    df[t_col] = pd.to_datetime(df[t_col], format=t_format)
    if t_org == 0:
        t_org = df[t_col][0]
    df[cname] = (df[t_col] - t_org).apply(lambda x: x.total_seconds())

    print("%inf:csv_trimtime:calculate_elapsed_time:min={},max={},mean={}".format(df[cname].min(), df[cname].max(), df[cname].mean()),
          file=sys.stderr)

    return df


def sort_time_column(df, sort_time_def):
    cvs = re.split(r"\s*(?<!\\):\s*", sort_time_def)
    cname = cvs[0]
    if len(cvs) < 2:
        t_format = "%Y-%m-%d %H:%M:%S"
    else:
        t_format = cvs[1]

    df[cname] = pd.to_datetime(df[cname], format=t_format)
    df.sort_values(by=cname, inplace=True)
    df.reset_index(inplace=True)

    return df


def do_rsampling(df, resample_defs, resample_func):

    cvs = re.split(r"\s*(?<!\\):\s*", resample_defs)
    if len(cvs) > 3:
        t_col = cvs[0]
        t_fmt = cvs[1]
        t_freq = cvs[2]
        columns_s = cvs[3]
        t_fmt = re.sub(r"\\", "", t_fmt)
    elif len(cvs) == 3:
        t_fmt = "%Y-%m-%d %H:%M:%S"
        t_col = cvs[0]
        t_freq = cvs[1]
        columns_s = cvs[2]
    else:
        print("??error:csv_trimtime:resampling:invalid definition:{}".format(resample_defs), file=sys.stderr)
        sys.exit(1)
    columns = re.split(r"\s*(?<!\\),\s*", columns_s)

    output_df = df[columns + [t_col]]

    output_df[t_col] = pd.to_datetime(df[t_col], format=t_fmt)
    output_df.set_index(t_col, inplace=True)

    if resample_func == "sum":
        output_df = output_df.resample(t_freq).sum()
    elif resample_func == "min":
        output_df = output_df.resample(t_freq).min()
    elif resample_func == "max":
        output_df = output_df.resample(t_freq).max()
    elif resample_func == "mean":
        output_df = output_df.resample(t_freq).mean()
    elif resample_func == "std":
        output_df = output_df.resample(t_freq).std()
    elif resample_func == "count":
        output_df = output_df.resample(t_freq).count()
    elif resample_func == "nearest":
        output_df = output_df.resample(t_freq).nearest()
    elif resample_func in RESAMPLE_METHOD_INTERPOLATE:
        if resample_func not in ["spline", "polynomial"]:
            output_df = output_df.resample(t_freq).interpolate(method=resample_func)
        else:
            output_df = output_df.resample(t_freq).interpolate(method=resample_func, order=3)

    output_df.fillna(0, inplace=True)
    return output_df


def do_reformat(df, reformat_def):

    cvs = re.split(r"\s*(?<!\\):\s*", reformat_def)
    if len(cvs) < 2:
        print("??error:csv_trimtime:reformat:invalid definition:{}".format(reformat_def), file=sys.stderr)
        sys.exit(1)
    cname = cvs[0]
    in_fmt = cvs[1]
    in_fmt = re.sub(r"\\", "", in_fmt)
    if len(cvs) > 2:
        out_fmt = cvs[2]
        out_fmt = re.sub(r"\\", "", out_fmt)
    else:
        out_fmt = None

    df[cname] = pd.to_datetime(df[cname], format=in_fmt)

    return df, out_fmt


def do_addtimecolumn(df, time_column_def):
    cvs = re.split(r"\s*(?<!\\):\s*", time_column_def)
    if len(cvs) < 2:
        print("??error:csv_trimtime:add time column:invalid definition:{}".format(time_column_def), file=sys.stderr)
        sys.exit(1)
    cname = cvs[0]
    t_start = cvs[1]
    t_freq = cvs[2]

    t_start = re.sub(r"\\", "", t_start)

    t_periods = len(df)

    df[cname] = pd.date_range(start=t_start, periods=t_periods, freq=t_freq)

    return df


def evaluate_timestamp(df, eval_def):
    cvs = re.split(r"\s*(?<!\\):\s*", eval_def)
    if len(cvs) < 2:
        print("??error:csv_trimtime:timestamp:invalid format {}".format(eval_def), file=sys.stderr)
        sys.exit(1)
    cname_0 = cvs[0]
    cname_1 = cvs[1]

    df[cname_0] = list(map(lambda x: x.timestamp(), pd.to_datetime(df[cname_1]).dt.to_pydatetime()))
    return df


def do_select_hours(df, select_hours_def):
    cvs = re.split(r"\s*(?<!\\):\s*", select_hours_def)
    if len(cvs) < 2:
        print("??error:csv_trimtime:select hours: invalid format {}".format(select_hours_def), file=sys.stderr)
        sys.exit(1)

    if len(cvs) > 2:
        t_col = cvs[0]
        t_fmt = cvs[1]
        t_range = cvs[2]
    else:
        t_col = cvs[0]
        t_range = cvs[1]
        t_fmt = None

    cvs = re.split(r"\s*(?<!\\),\s*", t_range)
    t_start = cvs[0]
    t_start = re.sub(r"\\", "", t_start)
    t_end = cvs[1]
    t_end = re.sub(r"\\", "", t_end)

    df[t_col] = pd.to_datetime(df[t_col], format=t_fmt)
    df.set_index(t_col, inplace=True)

    output_df = df.iloc[df.index.indexer_between_time(t_start, t_end, include_start=True, include_end=True), :]
    # columns = df.columns
    # output_df = pd.DataFrame()
    # for col in columns:
    #     if col != t_col:
    #         output_df[col] = df[col].between_time(t_start, t_end, include_start=True, include_end=True)

    return output_df


def do_select_datetime(df, select_dt_def):
    cvs = re.split(r"\s*(?<!\\):\s*", select_dt_def)
    if len(cvs) < 2:
        print("??error:csv_trimtime:select datetime: invalid format {}".format(select_dt_def), file=sys.stderr)
        sys.exit(1)

    if len(cvs) > 2:
        t_col = cvs[0]
        t_fmt = cvs[1]
        t_range = cvs[2]
    else:
        t_col = cvs[0]
        t_range = cvs[1]
        t_fmt = None

    cvs = re.split(r"\s*(?<!\\),\s*", t_range)
    t_start = cvs[0]
    t_start = re.sub(r"\\", "", t_start)
    t_end = cvs[1]
    t_end = re.sub(r"\\", "", t_end)

    t_start = dtt.strptime(t_start, t_fmt)
    t_end = dtt.strptime(t_end, t_fmt)

    df[t_col] = pd.to_datetime(df[t_col], format=t_fmt)
    # df.set_index(t_col, inplace=True)

    output_df = df.loc[(df[t_col] >= t_start) & (df[t_col] <= t_end)]

    return output_df


def do_get_range_time(df, range_time_def):
    cvs = re.split(r"\s*(?<!\\):\s*", range_time_def)
    if len(cvs) < 2:
        print("??error:csv_trimtime:get range of time:invalid definition:{}".format(range_time_def), file=sys.stderr)
        sys.exit(1)
    cname = cvs[0]
    if len(cvs) > 2:
        in_fmt = cvs[1]
        t_unit = cvs[2]
        in_fmt = re.sub(r"\\", "", in_fmt)
    else:
        in_fmt = None
        t_unit = cvs[1]

    df[cname] = pd.to_datetime(df[cname], format=in_fmt)
    dt_max = df[cname].max()
    dt_min = df[cname].min()
    dt = dt_max - dt_min
    dt = dt.total_seconds()
    unit_s = "seconds"
    if t_unit.upper() == "D":
        dt = dt / (60 * 60 * 24)
        unit_s = "days"
    elif t_unit.upper() == "H":
        dt = dt / (60 * 60)
        unit_s = "hours"
    elif t_unit.upper() == "M":
        dt = dt / (60)
        unit_s = "mins"
    elif t_unit.upper() != "S":
        print("??error:csv_trimtime:get time of range:invalid unit:{}".format(t_unit), file=sys.stderr)
        sys.exit(1)

    return dt, cname, unit_s, dt_max, dt_min


if __name__ == "__main__":
    args = init()
    csv_file = args.csv_file
    output_file = args.OUTPUT

    if csv_file == "-":
        csv_file = sys.stdin

    # sort time
    sort_time_def = args.TSORT

    # range of time
    range_time_defs = args.GRANGE

    # select hours
    t_select_hours = args.TSELECT_HOURS

    # select hours
    t_select_dt = args.TSELECT

    # timestamp
    tstamp_def = args.TSTAMP

    # add time series
    time_column_def = args.TIMECOLUMN

    # reformat
    refmt_def = args.REFORMAT

    # elapsed time
    elapsed_time_def = args.ETIME

    # gap
    gap_s = args.GAP
    gap_defs = []
    if gap_s is not None:
        gap_defs = re.split(r"\s*(?<!\\),\s*", gap_s)

    # time gap
    timegap_s = args.TGAP
    timegap_defs = []
    if timegap_s is not None:
        timegap_defs = re.split(r"\s*(?<!\\),\s*", timegap_s)

    # time diff
    time_diff = args.TDIFF

    # time frequency
    ch_timefreqs_s = args.CHTFREQ
    ch_timefreqs = []
    if ch_timefreqs_s is not None:
        ch_timefreqs = re.split(r"\s*(?<!\\),\s*", ch_timefreqs_s)

    # resampling
    resample_defs = args.RESAMPLE
    resample_func = args.RESAMPLE_FUNC

    #--- processing
    csv_df = pd.read_csv(csv_file)

    out_date_fmt = None

    if range_time_defs is not None:
        r_time, cname, unit_s, dt_max, dt_min = do_get_range_time(csv_df, range_time_defs)
        print("%inf:csv_trimtime:get time of range:{}:max={},min={}:perid={} {}".format(cname, dt_max, dt_min, r_time, unit_s))
        sys.exit(0)

    if sort_time_def is not None:
        print("%Inf:csv_trimtime:sort datetime:[{}]".format(sort_time_def), file=sys.stderr)
        csv_df = sort_time_column(csv_df, sort_time_def)

    # timestamp
    if tstamp_def is not None:
        csv_df = evaluate_timestamp(csv_df, tstamp_def)

    # time series
    if time_column_def is not None:
        df = do_addtimecolumn(csv_df, time_column_def)

    # reformat
    if refmt_def is not None:
        df, out_date_fmt = do_reformat(csv_df, refmt_def)

    if elapsed_time_def is not None:
        print("%Inf:csv_trimtime:calculate elapsed time:[{}]".format(elapsed_time_def), file=sys.stderr)
        csv_df = calculate_elapsed_time(csv_df, elapsed_time_def)

    if len(gap_defs) > 0:
        print("%Inf:csv_trimtime:groupby gap:[{}]".format(gap_defs), file=sys.stderr)
        csv_df = groupby_value_gap(csv_df, gap_defs)

    if len(timegap_defs) > 0:
        print("%Inf:csv_trimtime:groupby time gap:[{}]".format(timegap_defs), file=sys.stderr)
        csv_df = groupby_time_gap(csv_df, timegap_defs)

    if time_diff is not None:
        print("%Inf:csv_trimtime:calculate time diff:[{}]".format(time_diff), file=sys.stderr)
        csv_df = calculate_time_diff(csv_df, time_diff)

    if len(ch_timefreqs) > 0:
        print("%Inf:csv_trimtime:changing time frequency:[{}]".format(ch_timefreqs), file=sys.stderr)
        csv_df = change_time_frequency(csv_df, ch_timefreqs)

    csv_index = False
    if resample_defs is not None:
        print("%Inf:csv_trimtime:resampling:[{}]".format(resample_defs), file=sys.stderr)
        csv_df = do_rsampling(csv_df, resample_defs, resample_func)
        csv_index = True

    if t_select_dt is not None:
        print("%Inf:csv_trimtime:select datetime:[{}]".format(t_select_dt), file=sys.stderr)
        csv_df = do_select_datetime(csv_df, t_select_dt)

    if t_select_hours is not None:
        print("%Inf:csv_trimtime:select hours:[{}]".format(t_select_hours), file=sys.stderr)
        csv_df = do_select_hours(csv_df, t_select_hours)
        csv_index = True

    csv_df.to_csv(output_file, index=csv_index, date_format=out_date_fmt)
