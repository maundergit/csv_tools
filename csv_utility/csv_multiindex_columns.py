#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_multiindex_columns.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-11-06 18:19:52>
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


def init():
    arg_parser = argparse.ArgumentParser(description="handle multiindex columns csv",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:


example:

cat test_multiindex_columns.csv
,,C,,,D,,
A,B,X,Y,Z,X,Y,Z
1,2,3,4,5,6,7,8
3,4,5,6,7,8,9,0

csv_multiindex_columns.py test_multiindex_columns.csv
,,C,C,C,D,D,D
A,B,X,Y,Z,X,Y,Z
1,2,3,4,5,6,7,8
3,4,5,6,7,8,9,0

cat test_multiindex_columns.csv
,,E,,,F,G,
,,C,,,D,,
A,B,X,Y,Z,X,Y,Z
1,2,3,4,5,6,7,8
3,4,5,6,7,8,9,0

 csv_multiindex_columns.py --only_header --nrows=3 test_multiindex_columns.csv
,,E,E,E,F,G,G
,,C,C,C,D,D,D
A,B,X,Y,Z,X,Y,Z
1,2,3,4,5,6,7,8

csv_multiindex_columns.py --nrows=3 --to_single test_multiindex_columns.csv |csvlook -I
| A | B | E_C_X | E_C_Y | E_C_Z | F_D_X | G_D_Y | G_D_Z |
| - | - | ----- | ----- | ----- | ----- | ----- | ----- |
| 1 | 2 | 3     | 4     | 5     | 6     | 7     | 8     |
| 3 | 4 | 5     | 6     | 7     | 8     | 9     | 0     |


'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))

    arg_parser.add_argument("--nrows", dest="NROWS", help="number of rows as header,default=2", type=int, metavar='INT', default=2)

    arg_parser.add_argument("--output", dest="OUTPUT", help="path of output file, default=stdout", metavar="FILE", default=sys.stdout)

    arg_parser.add_argument("--to_single", dest="SINGLE", help="convert single header for columns", action="store_true", default=False)
    arg_parser.add_argument("--only_header", dest="ONLYHEADER", help="parse only header rows", action="store_true", default=False)

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='files to read, if empty, stdin is used')
    args = arg_parser.parse_args()
    return args


def read_csv_of_multiindex_columns(filepath_or_buffer, header='infer', **kwargs):
    """FIXME! briefly describe function

    :param filepath_or_buffer: 
    :param header: 
    :returns: 
    :rtype: 
    :example:
input:
,,C,,,D,,
A,B,X,Y,Z,X,Y,Z
1,2,3,4,5,6,7,8
3,4,5,6,7,8,9,0

results:
         C        D
   A  B  X  Y  Z  X  Y  Z
0  1  2  3  4  5  6  7  8
1  3  4  5  6  7  8  9  0

    """
    # python - Pandas read multiindexed csv with blanks - Stack Overflow https://stackoverflow.com/questions/30322581/pandas-read-multiindexed-csv-with-blanks
    df = pd.read_csv(filepath_or_buffer, header=header, dtype='object', **kwargs)
    columns = pd.DataFrame(df.columns.tolist())
    if isinstance(header, list):
        for ih in header:
            columns.loc[columns[ih].str.startswith('Unnamed:'), ih] = np.nan
            columns[ih] = columns[ih].fillna(method='ffill')
            # mask = pd.isnull(columns[0])
            columns[ih] = columns[ih].fillna('')
    # columns.loc[mask, [0, 1]] = columns.loc[mask, [1, 0]].values
    df.columns = pd.MultiIndex.from_tuples(columns.to_records(index=False).tolist())

    return df


def multiindex_column_to_flat(df):
    columns = list(map(lambda x: re.sub(r"^_+", "", x.strip()), ["_".join(v) for v in df.columns.to_flat_index().tolist()]))
    columns = [re.sub(r"\s+", "_", v) for v in columns]
    df.columns = columns
    return df


if __name__ == "__main__":
    args = init()
    csv_file = args.csv_file
    output_file = args.OUTPUT

    nrows_headers = args.NROWS
    to_single = args.SINGLE
    only_header = args.ONLYHEADER

    if csv_file == "-":
        csv_file = sys.stdin

    header = list(range(nrows_headers))

    csv_params = {}
    if only_header:
        csv_params.update({"nrows": 1})
    csv_df = read_csv_of_multiindex_columns(csv_file, header=header, **csv_params)

    # print(csv_df)
    if to_single:
        csv_df = multiindex_column_to_flat(csv_df)

    csv_df.to_csv(output_file, index=False)
