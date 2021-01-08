#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_combine.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-11-02 19:40:25>
# Licence:
#  Copyright (c) 2021 Masaharu N. Akei
#
#  This software is released under the MIT License.
#    http://opensource.org/licenses/mit-license.php
# ----------------------------------------------------------------------
import argparse
import textwrap
import sys

from pathlib import Path

import re
import pandas as pd

VERSION = 1.0


def init():

    arg_parser = argparse.ArgumentParser(description="complement the defect of datas with csv datas, element-wise",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:
  This processes columns that have only numeric values.

  The bigger mode, smaller mode and etc are available for columns that have numeric values, others are done by combine_first.
  At the compare modes(lt,gt,and so on), NaN leads into False as result, always.

  About function that was given by '--function', that has two arguments of pandas.Series. see document of pandas.DataFrame.combine:
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.combine.html#pandas.DataFrame.combine
  When you use '--function', you may use '--prologe' to load external module:
    ex. '--prologe="import numpy as np;"' or '--prologe="import your_module;"'

    | mode     | numeric only | description                                   |
    | -------- | ------------ | --------------------------------------------- |
    | first    |              | combine_first                                 |
    | bigger   | O            | select bigger                                 |
    | smaller  | O            | select smaller                                |
    | function | O            | to do given function                          |
    | add      | O            | adding                                        |
    | sub      | O            | subtructing                                   |
    | mul      | O            | multipling                                    |
    | div      | O            | dividing                                      |
    | mod      | O            | modulo                                        |
    | pow      | O            | power                                         |
    | lt       | O            | results of 'less than' are True/False         |
    | le       | O            | results of 'less than equal' are True/False   |
    | gt       | O            | results of 'greater than' are True/False      |
    | ge       | O            | results of 'grater than equal' are True/False |
    | ne       | O            | results of 'not equal' are True/False         |
    | eq       | O            | results of 'equal' are True/False             |

  Second argument is a path of a second csv file or scalar float value.
  When scala value is given, second csv will be created with the same shape as first csv and have given value in all elements.
  Because of inefficiently, you should not use scala value as second argument for big csv data.

example:
  csv_combine.py --mode bigger t1.csv t2.csv| csvlook -I
  | A   | B   | C | D |
  | --- | --- | - | - |
  | 1.0 | 1.0 | 1 | a |
  | 3.0 | 4.0 | 5 | b |
  | 5.0 | 5.0 | 3 | c |
  | 6.0 |     | 4 | d |

  csv_combine.py --mode smaller t1.csv t2.csv| csvlook -I
  | A   | B   | C | D |
  | --- | --- | - | - |
  | 0.0 | 0.0 | 0 | a |
  | 2.0 | 2.0 | 0 | b |
  | 3.0 | 5.0 | 3 | c |
  | 6.0 |     | 4 | d |

  csv_combine.py --mode function --function "lambda s1,s2: s1 if s1.sum() > s2.sum() else s2" t1.csv t2.csv |csvlook -I
  | A   | B   | C | D |
  | --- | --- | - | - |
  | 0.0 | 1.0 | 1 | a |
  | 3.0 | 4.0 | 0 | b |
  | 5.0 | 5.0 | 3 | c |
  | 6.0 |     | 4 | d |

  csvlook -I t1.csv
  | A | B | C | D |
  | - | - | - | - |
  | 1 | 0 | 1 | a |
  | 2 | 2 | 0 | b |
  | 3 |   | 3 |   |
  |   |   | 4 | d |

  csvlook -I t2.csv
  | A | B | C | D |
  | - | - | - | - |
  | 0 | 1 | 0 | a |
  | 3 | 4 | 5 | b |
  | 5 | 5 |   | c |
  | 6 |   |   |   |

'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument(
        "--mode",
        dest="MODE",
        help="combine mode",
        choices=["first", "bigger", "smaller", "add", "sub", "mul", "div", "mod", "pow", "lt", "le", "gt", "ge", "ne", "eq", "function"],
        default="first")
    arg_parser.add_argument("--function", dest="FUNC", help="lambda function for function mode", type=str, metavar='EXP', default=None)
    arg_parser.add_argument("--prologe",
                            dest="PROLOGE",
                            help="pieces of python code to pre-load, for use in expression of '--function'.",
                            type=str,
                            metavar='CODE;[CODE;CODE;...]',
                            default=None)
    arg_parser.add_argument("--boolean_by_number",
                            dest="BNUM",
                            help="for logical results, use 1/0 instead of True/False",
                            action="store_true",
                            default=False)

    arg_parser.add_argument("--output_file",
                            dest="OUTPUT_FILE",
                            help="path of output file,default=stdout",
                            type=str,
                            metavar='FILE',
                            default=sys.stdout)

    arg_parser.add_argument('csv_file_1', metavar='CSV_FILE', help='first csv file to complement')
    arg_parser.add_argument('csv_file_2_or_value', metavar='CSV_FILE_or_VALUE', help='second csv file or scalar float value')
    # arg_parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    # arg_parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    args = arg_parser.parse_args()
    return args


def combine_bigger(s1, s2):
    # w1 = s1.fillna(0).mask(s1 < s2, 0)
    # w2 = s2.fillna(0).mask(s1 >= s2, 0)
    w1 = s1.mask(s1 < s2, 0)
    w2 = s2.mask(s1 >= s2, 0)
    return w1.add(w2, fill_value=0)


def combine_smaller(s1, s2):
    # w1 = s1.fillna(0).mask(s1 > s2, 0)
    # w2 = s2.fillna(0).mask(s1 <= s2, 0)
    w1 = s1.mask(s1 > s2, 0)
    w2 = s2.mask(s1 <= s2, 0)
    return w1.add(w2, fill_value=0)


def combine_fillna(s1, s2):
    s1.loc[s1.isna()] = s2.loc[s1.isna()]
    return s1


if __name__ == "__main__":
    args = init()
    csv_file_1 = args.csv_file_1
    csv_file_2_or_value = args.csv_file_2_or_value
    output_file = args.OUTPUT_FILE

    c_mode = args.MODE
    f_lambda = args.FUNC
    prologe = args.PROLOGE
    bool_by_num = args.BNUM

    if c_mode == "function" and f_lambda is not None:
        print("??error:csv_combine:for '--mode function', '--function' is rquired.", file=sys.stderr)
        sys.exit(1)
    if bool_by_num and c_mode not in ["lt", "le", "gt", "ge", "ne", "eq"]:
        print("#warn:csv_combine:'--boolean_by_number' is not available for this mode:{}".format(c_mode), file=sys.stderr)
    if prologe is not None and c_mode != "function":
        print("#warn:csv_combine:'--prologe' is not available for this mode:{}".format(c_mode), file=sys.stderr)
    if c_mode != "function" and f_lambda is not None:
        print("#warn:csv_combine:'--function' is not available for this mode:{}".format(c_mode), file=sys.stderr)
        sys.exit(1)

    if prologe is not None:
        pps = re.split(r'\s*;\s*', prologe)
        for pp in pps:
            if len(pp) == 0:
                continue
            print("%Inf:csv_uty:exec python code:{}".format(pp), file=sys.stderr)
            exec(pp)

    csv_df_1 = pd.read_csv(csv_file_1)
    if Path(csv_file_2_or_value).exists():
        csv_df_2 = pd.read_csv(csv_file_2_or_value)
    else:
        csv_df_2 = csv_df_1.copy()
        csv_df_2[csv_df_2.columns] = float(csv_file_2_or_value)

    if c_mode == "first":
        csv_df_1.combine_first(csv_df_2)
    else:  # numeric mode
        cols_set = set(csv_df_1.select_dtypes(include=['int16', 'int32', 'int64', 'float16', 'float32', 'float64']).columns) & set(
            csv_df_2.select_dtypes(include=['int16', 'int32', 'int64', 'float16', 'float32', 'float64']).columns)
        cols = list(cols_set)
        if c_mode == "bigger":
            csv_df_1[cols] = csv_df_1[cols].combine(csv_df_2[cols], combine_bigger)
        elif c_mode == "smaller":
            csv_df_1[cols] = csv_df_1[cols].combine(csv_df_2[cols], combine_smaller)
        elif c_mode == "add":
            csv_df_1[cols] = csv_df_1[cols].add(csv_df_2[cols], fill_value=0)
        elif c_mode == "sub":
            csv_df_1[cols] = csv_df_1[cols].sub(csv_df_2[cols], fill_value=0)
        elif c_mode == "mul":
            csv_df_1[cols] = csv_df_1[cols].mul(csv_df_2[cols], fill_value=0)
        elif c_mode == "div":
            csv_df_1[cols] = csv_df_1[cols].div(csv_df_2[cols], fill_value=0)
        elif c_mode == "mod":
            csv_df_1[cols] = csv_df_1[cols].mod(csv_df_2[cols], fill_value=0)
        elif c_mode == "pow":
            csv_df_1[cols] = csv_df_1[cols].pow(csv_df_2[cols], fill_value=0)
        elif c_mode == "lt":
            csv_df_1[cols] = csv_df_1[cols].lt(csv_df_2[cols])
        elif c_mode == "le":
            csv_df_1[cols] = csv_df_1[cols].le(csv_df_2[cols])
        elif c_mode == "gt":
            csv_df_1[cols] = csv_df_1[cols].gt(csv_df_2[cols])
        elif c_mode == "ge":
            csv_df_1[cols] = csv_df_1[cols].ge(csv_df_2[cols])
        elif c_mode == "ne":
            csv_df_1[cols] = csv_df_1[cols].ne(csv_df_2[cols])
        elif c_mode == "eq":
            csv_df_1[cols] = csv_df_1[cols].eq(csv_df_2[cols])
        elif c_mode == "function":
            func = eval(f_lambda)
            # csv_df_1[cols] = csv_df_1[cols].fillna(0)
            # csv_df_2[cols] = csv_df_2[cols].fillna(0)
            csv_df_1[cols] = csv_df_1[cols].combine(csv_df_2[cols], func)

        rest_cols = list((set(csv_df_1.columns) - cols_set) & set(csv_df_2.columns))
        # csv_df_1[rest_cols] = csv_df_1[rest_cols].combine(csv_df_2[rest_cols], combine_fillna)
        csv_df_1[rest_cols] = csv_df_1[rest_cols].combine_first(csv_df_2[rest_cols])

    if bool_by_num and c_mode in ["lt", "le", "gt", "ge", "ne", "eq"]:
        csv_df_1.replace({True: 1, False: 0}, inplace=True)

    csv_df_1.to_csv(output_file, index=False)
