#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_histogram.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-09-12 16:18:16>
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
import re

from pathlib import Path

import numpy as np
import pandas as pd

VERSION = 1.0


def init():
    # argparse --- コマンドラインオプション、引数、サブコマンドのパーサー  Python 3.8.5 ドキュメント https://docs.python.org/ja/3/library/argparse.html
    arg_parser = argparse.ArgumentParser(description="make histogram from csv file",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:
  '--range' and 'weight_column' are available for only numerical 'column'.
example:
  csv_histogram.py --nbins=100 --output=- big_sample_arb.csv  COL_0008|less
  csv_histogram.py --nbins=100 --output=- --range=0.5,1.0 big_sample_arb.csv  COL_0008 COL_0033|less
  csv_histogram.py --facets=B,C,D test_hist.csv E
  csv_histogram.py --facets=B,C,D test_hist.csv A

'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument("--nbins", dest="NBINS", help="number of bins, default=20", type=int, metavar='INT', default=20)
    arg_parser.add_argument("--range", dest="XRANGE", help="range of x", type=str, metavar='LOWER_X,UPPER_X', default=None)

    arg_parser.add_argument("--facets", dest="FACETS", help="facets", type=str, metavar="COLUMN[,COLUMN...]")

    arg_parser.add_argument("--output", dest="OUTPUT", help="path of output file", type=str, metavar="FILE")

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='files to read, if empty, stdin is used')
    arg_parser.add_argument('column', metavar='COLUMN', help='name of column to make histogram')
    arg_parser.add_argument('weight_column', metavar='WEIGHT_COLUMN', nargs="?", help='name of column as weight')
    args = arg_parser.parse_args()
    return args


FACETS_COUNT_LIMIT = 10


def categs_hist_facets(hist_df, input_df, column_name, facets_columns):
    for fc in facets_columns:
        nf = len(input_df[fc].value_counts().index)
        if nf > FACETS_COUNT_LIMIT:
            print("??Error:csv_histogram:number of uniq items is too many  for {}".format(fc), file=sys.stderr)
            sys.exit(1)
        f_items = list(input_df[fc].value_counts(sort=True).index)
        for fi in f_items:
            h_ds = input_df.loc[input_df[fc] == fi, column_name].value_counts()
            h_ds.name = "{}={}".format(fc, fi)
            h_ds.index.name = "category"
            hist_df = pd.concat([hist_df, h_ds], axis=1)
            hist_df.index.name = "category"
            hist_df.fillna(0, inplace=True)

    return hist_df


def number_hist_facets(hist_df, input_df, column_name, facets_columns, bins, weight_column):
    for fc in facets_columns:
        nf = len(input_df[fc].value_counts().index)
        if nf > FACETS_COUNT_LIMIT:
            print("??Error:csv_histogram:number of uniq items is too many  for {}".format(fc), file=sys.stderr)
            sys.exit(1)
        f_items = sorted(list(input_df[fc].value_counts(sort=True).index))
        for fi in f_items:
            h_df_2 = input_df.loc[input_df[fc] == fi]
            nphist_arg = {"bins": bins}
            if weight_column is not None:
                nphist_arg.update({"weights": np.array(h_df_2[weight_column])})
            hist, bins = np.histogram(np.array(h_df_2[column_name]), **nphist_arg)
            cname = "{}={}".format(fc, fi)
            h_df = pd.DataFrame(columns=["bin", cname])
            h_df.set_index("bin")
            h_df["bin"] = bins[:-1]
            h_df[cname] = hist
            hist_df = hist_df.merge(h_df)

    return hist_df


if __name__ == "__main__":
    args = init()
    csv_file = args.csv_file
    output_file = args.OUTPUT
    column_name = args.column
    weight_column = args.weight_column
    facets_columns_s = args.FACETS

    nbins = args.NBINS
    nphist_arg = {"bins": nbins}

    xrange_s = args.XRANGE
    if xrange_s is not None:
        cvs = list(map(float, re.split(r",", xrange_s)))
        nphist_arg.update({"range": cvs})
    facets_columns = []
    if facets_columns_s is not None:
        facets_columns = re.split(r"\s*,\s*", facets_columns_s)

    if output_file is None:
        if csv_file != "-":
            output_file = Path(csv_file).stem + "_hist.csv"
        else:
            output_file = sys.stdout
    elif output_file == "-":
        output_file = sys.stdout

    if csv_file == "-":
        csv_file = sys.stdin

    csv_df = pd.read_csv(csv_file)

    if csv_df[column_name].dtype == object:
        print("-- un-numerical mode:", file=sys.stderr)
        h_ds = csv_df[column_name].value_counts(sort=True)
        h_ds.name = "counts"
        h_ds.index.name = "category"
        h_df = pd.DataFrame(h_ds)
        if len(facets_columns) > 0:
            h_df = categs_hist_facets(h_df, csv_df, column_name, facets_columns)
        h_df.to_csv(output_file)
    else:
        if weight_column is not None:
            nphist_arg.update({"weights": np.array(csv_df[weight_column])})
        hist, bins = np.histogram(np.array(csv_df[column_name]), **nphist_arg)
        h_df = pd.DataFrame(columns=["bin", "counts"])
        h_df.set_index("bin")
        h_df["bin"] = bins[:-1]
        h_df["counts"] = hist
        if len(facets_columns) > 0:
            h_df = number_hist_facets(h_df, csv_df, column_name, facets_columns, bins, weight_column)
        h_df.to_csv(output_file, index=False)
        print("-- statistical status for numerical datas", file=sys.stderr)
        print(csv_df[column_name].describe(), file=sys.stderr)

    if output_file != sys.stdout:
        print("-- {} was created".format(output_file), file=sys.stderr)
