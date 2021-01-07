#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_query.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-09-01 17:26:16>
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


def init():
    arg_parser = argparse.ArgumentParser(description="do query for CSV data",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:
 for encoding, see "Codec registry and base classes https://docs.python.org/3/library/codecs.html#standard-encodings"
 you can use str.contains(),str.endswith(),str.startswith(),str.match() and 'in' in query string.

 When '--query_file' was used, those lines were used as query string as joining with 'or'.
 In query file, lines those starts with '#' are ignored as comment lines.

example:
 csv_query.py big_sample_arb.csv 'COL_0002=="001001" and COL_0006=="PAT001"'
 csv_query.py big_sample_arb.csv 'COL_0002=="001001" and COL_0006.str.contains("PAT001")'
 csv_query.py --query_file=test_query.txt test1.csv

 cat test_query.txt
 # test
 B==2
 C==6

'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument("--encoding", dest="ENCODE", help="encoding, default=utf-8", type=str, metavar='STR', default="utf-8")
    arg_parser.add_argument("--query_file", dest="QFILE", help="path of query file", type=str, metavar='FILE', default=None)
    arg_parser.add_argument("--columns",
                            dest="COLUMNS",
                            help="names of colunmns to ouput, default=all",
                            type=str,
                            metavar='COLUMNS[,COLUMNS,[COLUMNS,...]]',
                            default="all")
    arg_parser.add_argument("--output", dest="OUTPUT", help="path of output, default is stdout", type=str, metavar='STR', default=None)

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='path of csv file')
    arg_parser.add_argument('query', metavar='STR', help='query string', nargs='?')
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    args = init()
    csv_file = args.csv_file
    query_file = args.QFILE
    query = args.query

    if query_file is None and query is None:
        print("??error:csv_query: 'query' string or '--uery_file' must be given", file=sys.stderr)
        sys.exit(1)

    csv_output = args.OUTPUT
    if csv_output is None:
        csv_output = sys.stdout
    if csv_file == "-":
        csv_file = sys.stdin

    encode = args.ENCODE
    columns = args.COLUMNS

    if query_file is not None:
        with open(query_file, 'r') as f:
            qs = [v.strip() for v in f.readlines() if not v.startswith('#')]
            query = " or ".join(["({})".format(v) for v in qs if len(v) != 0])
            print("%inf:csv_query:query was read from '{}':{}".format(query_file, query), file=sys.stderr)

    csv_df = pd.read_csv(csv_file, encoding=encode)

    try:
        res_df = csv_df.query(query, engine="python")
    except TypeError as e:
        print("??Error:csv_query:query '{}':{}".format(query, e), file=sys.stderr)
        print("-- data types in csv", file=sys.stderr)
        print(textwrap.indent(str(csv_df.dtypes), ">> "), file=sys.stderr)
        sys.exit(1)

    if columns == "all":
        columns = list(res_df.columns)
    else:
        columns = re.split(r"\s*,\s*", columns)

    res_df[columns].to_csv(csv_output, encoding=encode, index=False)
