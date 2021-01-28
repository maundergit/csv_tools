#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_dummy.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-08-14 19:16:36>
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

import json
import datetime as dt
import numpy as np
import csv
import pandas as pd

VERSION = 1.0

ARBITRARITY_TABLE = [
    "fixed:FIXED", "hex", "int", "rand", "datetime", "list:{\"001001\":1,\"010010\":1,\"100100\":1,\"000001\":4}",
    "list:[\"PAT001\",\"PAT002\",\"PAT003\",\"PAT004\",\"PAT005\"]", "format:\"file_{row}_{col}.txt\"", "format:\"cycle{random:04d}\"",
    "format:\"TIME_{time}\"", "random.beta(1,2)"
]


def init():
    arg_parser = argparse.ArgumentParser(description="generate dummy data of csv",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''

remark:
  when '--mode=header' was given, you can use 'np.random.*'. 
  see "Random Generator  NumPy v1.19 Manual https://numpy.org/doc/stable/reference/random/generator.html"

  In header mode, 
  'index' means serial number with 0-base, 'int' means ic+ncols+ir, 
  'rand' means uniform random number in [0,1], 'random.*' means using function in np.random.*,.
  'datetime' means time string of now()+(ir+ic) seconds or frequentry time string with 'datetime:<time string>[:<frequency>]', '<frequency>' is optional.
  '<time string>' is formatted with '%Y-%m-%d %H:%M:%S'. Note: ':' must be esacped by back-slash, see exmple.
  about '<frequency>', see ' pandas documentation https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases'
  'fixed' means fixed value, 
  'list' means random choiced value in list or dictionary with given probabilites.
  'format' means formatted string with 'row', 'col', 'time', 'random' variables, where 'time' is current time(%H%M%S) and 'random' is randomized integer in [0,100].

example:
  csv_dummy.py --mode header --headers bit-pattern-headers.txt 200 > bit-pattern-headers.csv
  csv_dummy.py --headers=headers.txt --mode=header 5 
ABC000,ABC001,ABC002,ABC003,ABC004,ABC005,ABC006,ABC007,ABC008,ABC009,ABC010
0,1,2020-11-01 09:48:38,2020-12-01 08:05:10,ABCDEF,"A0001",0.9769355181667144,"00000007",file_000_008_068_094836.txt,A0001,13
1,16,2020-11-01 09:48:39,2020-12-01 13:05:10,ABCDEF,"A0001",0.9537397926065723,"00010007",file_001_008_043_094836.txt,B0010,13
2,31,2020-11-01 09:48:40,2020-12-01 18:05:10,ABCDEF,"A0001",0.6544350953595085,"00020007",file_002_008_003_094836.txt,B0010,5
3,46,2020-11-01 09:48:41,2020-12-01 23:05:10,ABCDEF,"A0001",0.2262489413244111,"00030007",file_003_008_054_094836.txt,B0010,17
4,61,2020-11-01 09:48:42,2020-12-02 04:05:10,ABCDEF,"A0001",0.23743226355108915,"00040007",file_004_008_022_094836.txt,A0001,17

  header.txt example:
  ABC000 index
  ABC001 int
  ABC002 datetime
  ABC003 datetime:2020-12-01 08\:05\:10:5h
  ABC004 fixed: ABCDEF
  ABC005 q:list:["A0001","A0001","A0001","A0001","B0010"]
  ABC006 rand
  ABC007 q:hex
  ABC008 format:"file_{row:03d}_{col:03d}_{random:03d}_{time}.txt"
  ABC009 list:{"A0001":3,"B0010":2}
  ABC010 list:[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]
  ABC011 random.beta(0.2,10.)
  ABC012 random.normal()
  ABC013 random.exponential()
  ABC014

'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument("--output", dest="OUTPUT", type=str, help="output file", metavar="FILE", default=None)
    arg_parser.add_argument("--quote", dest="QUOTE", help="quoteing value of each cell", action="store_true", default=False)
    arg_parser.add_argument("--mode",
                            dest="MODE",
                            help="value mode of each cell: hex={ir:04x}{ic:04x}, rand=random, ind=continus integer, " +
                            "header=definition in headers file",
                            type=str,
                            choices=["rand", "int", "hex", "header", "arbitrarily"],
                            default="hex")
    arg_parser.add_argument("--headers",
                            dest="HEADERS",
                            help="list file that has names of columns: csv format as one records or each name per line",
                            type=str,
                            metavar="FILE",
                            default=None)

    arg_parser.add_argument('number_of_rows', metavar='ROWS', help='number of data rows', type=int)
    arg_parser.add_argument('number_of_columns', metavar='COLS', help='number of columns', type=int, nargs='?', default=None)
    args = arg_parser.parse_args()
    return args


def make_distribution(ctype):
    """FIXME! briefly describe function

    :param ctype: 
    :returns: 
    :rtype: 

    Random Generator  NumPy v1.19 Manual https://numpy.org/doc/stable/reference/random/generator.html
    """
    m = re.match(r"random.(\w+)\((.*)\)", ctype)
    result = None
    if m is not None:
        result = eval("np.random." + ctype[7:])

    return result


def make_column(c_type, ir, ic):
    """derive value of cell for (ir,ic)

    :param c_type: type cell
    :param ir: index of row
    :param ic: index of column
    :returns: value of cell
    :rtype: str
    :remark:

    int
    rand
    date
    fixed:ABCDEF
    list:["A","B","C"]
    list:{"A":3,"B":3,"C":4}
    hex
    index
    format:"file_{row}_{col}.txt"

    """
    result = ""

    # quotation
    if c_type is not None and c_type.startswith("q:"):
        sep = '"'
        c_type = c_type[2:]
    else:
        sep = ""

    # each type
    if c_type is None or c_type == "hex":
        result = "{:04x}{:04x}".format(ir, ic)
    elif c_type == "index":
        result = str(ir)
    elif c_type == "int":
        result = str(ic + ncols * ir)
    elif c_type == "rand":
        result = str(np.random.random())
    elif c_type.startswith("random."):
        res = make_distribution(c_type)
        if res is not None:
            result = str(res)
        else:
            print("??Error:csv_dummy:unknown type for {}:{}".format(ic, c_type), file=sys.stderr)
    elif c_type.startswith("datetime"):
        result = (dt.datetime.now() + dt.timedelta(seconds=ir + ic)).strftime("%Y-%m-%d %H:%M:%S")
    elif c_type[0:6] == "fixed:":
        cvs = re.split(r'\s*:\s*', c_type)
        result = cvs[1]
    elif c_type[0:5] == "list:":
        try:
            cvs = json.loads(c_type[5:])
        except json.decoder.JSONDecodeError as e:
            print("%error:csv_dump:invalid format:{}:please check '[' or '{{ or quotation'".format(c_type[5:]), file=sys.stderr)
            sys.exit(1)
        if isinstance(cvs, dict):
            cvs = sum([[v] * cvs[v] for v in cvs.keys()], [])

        # idx = np.random.randint(0, len(cvs))
        # result = str(cvs[idx])
        result = str(np.random.choice(cvs, 1)[0])
    elif c_type[0:7] == "format:":
        fmt = c_type[7:].strip('"')
        tt = dt.datetime.now().strftime("%H%M%S")
        rint = np.random.randint(0, 100)
        result = fmt.format(row=ir, col=ic, time=tt, random=rint)
    else:
        print("??Error:csv_dummy:unknown type for {}:{}".format(ic, c_type), file=sys.stderr)
    result = sep + result + sep
    return result


def read_headers(hfile):
    """read definitin of columns from header file

    :param hfile: path of header file
    :returns: name of columns, definition of columns
    :rtype: tuple(list,list)

    """
    lines = []
    with open(hfile, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith("#"):
                continue
            if len(line) > 0:
                lines.append(line)
    if len(lines) == 1:
        cols = re.split(r'\s*,\s*', lines[0])
    else:
        cols = lines

    h_result = []
    t_result = []
    for c in cols:
        cvs = re.split(r'\s+', c, maxsplit=1)
        if len(cvs) > 1:
            h_result.append(cvs[0])
            t_result.append(cvs[1])
        else:
            h_result.append(cvs[0])
            t_result.append(None)

    return h_result, t_result


def trim_datetime(df, col_names, header_definitions):
    nrows = len(df)
    ncols = len(df.columns)
    for col, hdef in zip(col_names, header_definitions):
        # datetime:star_time:frequency
        # datetime:2020-11-01 08\:01\:02:5h
        if hdef is None:
            continue
        if hdef.startswith("datetime:"):
            cvs = re.split(r"(?<!\\):", hdef)
            if len(cvs) < 2:
                print("??error:csv_dummy:invalid definition:column={},definition={}".format(col, hdef), file=sys.stderr)
                sys.exit(1)
            if len(cvs) < 3:
                start_time = cvs[1].replace("\\", "")
                st = dt.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                df[col] = pd.date_range(st, periods=nrows, freq='{}s'.format(ncols))
            else:
                start_time = cvs[1].replace("\\", "")
                t_freq = cvs[2]
                st = dt.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                df[col] = pd.date_range(st, periods=nrows, freq=t_freq)
    return df


if __name__ == "__main__":
    args = init()
    nrows = args.number_of_rows
    ncols = args.number_of_columns
    quote = args.QUOTE
    output = args.OUTPUT
    mode = args.MODE
    hfile = args.HEADERS

    if hfile is None and ncols is None:
        print("??Error:csv_dummy:wheather number of columns or '--headers' msut be defined.", file=sys.stderr)
        sys.exit(1)

    if mode == "header" and hfile is None:
        print("??Error:csv_dummy:header mode was required, but header file was not given", file=sys.stderr)
        sys.exit(1)

    if output is not None:
        output_f = open(output, "w")
    else:
        output = sys.stdout
    if hfile is not None:
        CS, TS = read_headers(hfile)
        if ncols is not None and ncols != len(CS):
            print("#warn:csv_dummy:number of columns dose not match between argument:{} and ones:{} in header file".format(
                ncols, len(CS)),
                  file=sys.stderr)
            ncols = len(CS)
        elif ncols is None:
            ncols = len(CS)
    else:
        CS = []
        TS = []
        for ic in range(ncols):
            CS.append("COL_{:04d}".format(ic))

    if mode == "arbitrarily":
        print("%info:csv_dummy:arbitrarily mode:header definition will be radomly seletcted from :{}".format(ARBITRARITY_TABLE),
              file=sys.stderr)
        TS = ["index"]
        TS.extend([np.random.choice(ARBITRARITY_TABLE, 1)[0] for i in range(ncols - 1)])

    # print out headers
    # print(",".join(CS), file=output)
    columns = CS

    if quote:
        if mode == "header":
            print("#warn:csv_dummy:in header mode, quote must be defined in header file.", file=sys.stderr)
        sep = '"'
    else:
        sep = ""

    rows_data = []
    for ir in range(nrows):
        print("-- processing row :{}".format(ir), end="\r", file=sys.stderr)
        if mode == "rand":
            CS = np.random.rand(ncols).tolist()
            CS = [sep + str(v) + sep for v in CS]
        elif mode == "int":
            CS = [ic + ncols * ir for ic in range(ncols)]
            CS = [sep + str(v) + sep for v in CS]
        elif mode == "header" or mode == "arbitrarily":
            CS = [make_column(v, ir, ic) for ic, v in enumerate(TS)]
        else:
            CS = []
            for ic in range(ncols):
                CS.append("{}{:04x}{:04x}{}".format(sep, ir, ic, sep))

        # print out each row
        # print(",".join(CS), file=output)
        rows_data.append(CS)

    csv_df = pd.DataFrame(rows_data, columns=columns)
    if len(TS) > 1:
        csv_df = trim_datetime(csv_df, columns, TS)
    csv_df.to_csv(output, index=False, quoting=csv.QUOTE_NONE)
    print("", file=sys.stderr)
