#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_stack_trime.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-09-09 18:07:11>
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

from pathlib import Path

import pandas as pd

VERSION = 1.0

# 多重意味付けカラムの分解


def init():
    arg_parser = argparse.ArgumentParser(description="split one column, that has multiple meaning, into some columns",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:
  columns definitions
      old_column_name:new_column_name:append_column=fixed_value:append_column_name=fixed_value....
  the appended_column may be used as a category that was derived from the old_colun_name as one of some meanings,
  and may be used as facet or category of csv_plot_*.

  If argument of '--definition' or '--columns' was started with '@', then those are read from the file.

  if a fixed_value starts with '@', then the remained value without '@' was treated as a column name, 
  so the appended column has the copy of the column, that may mean an attribute column that was BINDED to the old_column_name.
    ex. Cat1_Attr,Cat2_Attr,Attribute,Catgeory1_value,Category2_value 
        => Category1_value:value:Category=1:Attr=@Cat1_Attr,Category2_value:value:Category=2:Attr=@Cat2_Attr

  if more new_columns were given simulitaneously, there will be NaN in each others(see example).

example1:
  csv_stack_trime.py --definition=P1C1:C1:P=P1,P1C2:C2:P=P1,P2C1:C1:P=P2,P2C2:C2:P=P2 --include=N --output=- test3.csv

  input:
  P1C1,P1C2,P2C1,P2C2,N
  1,0,1,0,A
  1,0,0,1,B
  1,0,1,0,C
  1,0,1,0,D

  output:
  C1,C2,N,P
  1,,A,P1
  1,,B,P1
  1,,C,P1
  1,,D,P1
  ,0,A,P1
  ,0,B,P1
  ,0,C,P1
  ,0,D,P1
  1,,A,P2
  0,,B,P2
  1,,C,P2
  1,,D,P2
  ,0,A,P2
  ,1,B,P2
  ,0,C,P2
  ,0,D,P2

example2:
  sv_stack_trime.py --definition=@csv_stack_trim_defs.txt --include=COL3,COL4 csv_stack_trime.csv
  col_defs="COL1:NEW_COL1:COLA=ABC:COLB=CDEF,COL2:NEW_COL2:COLA=ZXY:COLC=1234:COLD=@COL7"
  inc_cols="COL3,COL4"
  csv_stack_trime.py --definition=${col_defs} --include=${inc_cols} csv_stack_trime.csv | csvlook -I

  input:
  COL1,COL2,COL3,COL4,COL5,COL6,COL7
  1,2,3,4,5,6,A
  7,8,9,10,11,12,B
  13,14,15,16,17,18,C
  19,20,21,22,23,24,D

  output:
  | COL3 | COL4 | COLA | COLB | COLC | COLD | NEW_COL1 | NEW_COL2 |
  | ---- | ---- | ---- | ---- | ---- | ---- | -------- | -------- |
  | 3.0  | 4.0  | ABC  | CDEF |      |      | 1        |          |
  | 9.0  | 10.0 | ABC  | CDEF |      |      | 7        |          |
  | 15.0 | 16.0 | ABC  | CDEF |      |      | 13       |          |
  | 21.0 | 22.0 | ABC  | CDEF |      |      | 19       |          |
  | 3.0  | 4.0  | ZXY  |      | 1234 | A    |          | 2        |
  | 9.0  | 10.0 | ZXY  |      | 1234 | B    |          | 8        |
  | 15.0 | 16.0 | ZXY  |      | 1234 | C    |          | 14       |
  | 21.0 | 22.0 | ZXY  |      | 1234 | D    |          | 20       |


'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument("--include",
                            dest="INC_COLS",
                            help="included columns, with csv format",
                            type=str,
                            metavar='COLUMNS[,COLUMNS...]',
                            default=None)
    arg_parser.add_argument("--definition",
                            dest="DEFN",
                            help="definition string to make translation",
                            type=str,
                            metavar='OLD_COL:NEW_COL:APPEND_COL=VALUE[:...]',
                            required=True)
    arg_parser.add_argument("--columns",
                            dest="OUTPUT_COLS",
                            help="list of columns at output",
                            type=str,
                            metavar='COL1,COL2,...',
                            default=None)

    arg_parser.add_argument("--output", dest="OUTPUT", help="path of output file", type=str, metavar="FILE", default=None)

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='files to read, if empty, stdin is used')
    args = arg_parser.parse_args()
    return args


def parse_columns(col_defs):
    """parse definition of columns

    :param col_defs: 
    :returns: 
    :rtype: 

    """
    # old_col ->{"rename":new_col,"append":{"col_1":"value1","col_2":"value2"}}

    print("%Inf:csv_stack_trim:definitions:{}".format(col_defs), file=sys.stderr)
    trans_tab = {}
    new_columns = []
    for cd in col_defs:
        cds = re.split(r'(?<!\\):', cd)
        if len(cds) < 2:
            print("??error:csv_stack_trim: invalid definition:{}".format(cds), file=sys.stderr)
            sys.exit(1)
        app_tabs = {}
        for scd in cds[2:]:
            scds = re.split(r'(?<!\\)=', scd)
            if len(scds) > 1:
                app_tabs[scds[0]] = scds[1]
                new_columns.append(scds[0])
            else:
                print("#warn:csv_stack_trim:unknown format of definition:{}".format(scd), file=sys.stderr)
            trans_tab[cds[0]] = {"rename": cds[1], "append": app_tabs}
            new_columns.append(cds[1])

    new_columns = list(set(new_columns))
    return new_columns, trans_tab


def read_defs_from_file(path_of_defs):
    lines = []
    with open(path_of_defs, 'r') as f:
        for line in f.readlines():
            line = line.rstrip()
            if line.startswith("#") or len(line) == 0:
                continue
            lines.append(line)

    result = ",".join(lines)

    return result


if __name__ == "__main__":
    args = init()
    csv_file = args.csv_file
    output_file = args.OUTPUT
    col_definitions = args.DEFN
    inc_cols_s = args.INC_COLS
    output_cols_s = args.OUTPUT_COLS

    output_cols = []
    if output_cols_s is not None:
        output_cols = re.split(r"\s*,\s*", output_cols_s)

    if output_file is None:
        if csv_file == "-":
            output_file = sys.stdout
        else:
            output_file = Path(csv_file).stem + "_ST.csv"
    elif output_file == "-":
        output_file = sys.stdout
    if csv_file == "-":
        csv_file = sys.stdin

    if col_definitions.startswith('@'):
        col_definitions = read_defs_from_file(col_definitions[1:])
    if inc_cols_s is not None and inc_cols_s.startswith('@'):
        inc_cols_s = read_defs_from_file(inc_cols_s[1:])

    col_defs = re.split(r"\s*(?<!\\),\s*", col_definitions)
    inc_cols = []
    if inc_cols_s is not None:
        inc_cols = re.split(r"\s*(?<!\\),\s*", inc_cols_s)

    new_cs, trans_tables = parse_columns(col_defs)

    csv_df = pd.read_csv(csv_file)

    # check names of columns
    for col in list(trans_tables.keys()) + inc_cols:
        if col not in csv_df.keys():
            print("??Error:csv_stack_trim:column={} was not found in source csv".format(col), file=sys.stderr)
            sys.exit(1)

    res_df = pd.DataFrame(columns=new_cs)
    # old_col ->{"rename":new_col,"append":{"col_1":"value1","col_2":"value2"}}
    for col, tt in trans_tables.items():
        w_df = pd.DataFrame()
        if tt["rename"] is not None and len(tt["rename"]) > 0:
            cname = tt["rename"]
        else:
            cname = col
        w_df[cname] = csv_df[col]
        if inc_cols is not None and len(inc_cols) > 0:
            # w_df[inc_cols] = csv_df[inc_cols].astype(str)
            w_df[inc_cols] = csv_df[inc_cols]
        for app_col, val in tt["append"].items():
            if val.startswith("@"):
                w_df[app_col] = csv_df[val[1:]]
            else:
                w_df[app_col] = val

        res_df = pd.concat([res_df, w_df], ignore_index=True, sort=True)

    if len(output_cols) > 0:
        cols = output_cols
    else:
        cols = sorted(res_df.columns)
    res_df.to_csv(output_file, index=False, columns=cols)
    if output_file != sys.stdout:
        print("-- {} was created.".format(output_file), file=sys.stderr)
