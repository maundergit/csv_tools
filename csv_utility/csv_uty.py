#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_uty.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-09-17 16:19:37>
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
from distutils.version import LooseVersion

import json

import numpy as np

import pandas as pd

VERSION = 1.0
PANDAS_MIN_VERSION = "1.1.3"
if LooseVersion(PANDAS_MIN_VERSION) > LooseVersion(pd.__version__):
    print("??Error:csv_uty:padnas version must be newer than {}.".format(PANDAS_MIN_VERSION), file=sys.stderr)
    sys.exit(1)

OUTPUT_FORMAT_DESC = {
    "csv": "comma-separated values (csv) file",
    "hdf": "HDF5 file using HDFStore",
    "parquet": "the binary parquet format, that reuires pyarrow module",
    "pickel": "Pickle (serialize) object to file",
    "json": "JSON string",
    "feather": "binary Feather format, that requires pyarrow module",
    "stata": "Stata dta format"
}
OUTPUT_FORMAT = list(OUTPUT_FORMAT_DESC.keys())
OUTPUT_REQUIRED_FILE = ["hdf", "parquet", "pickel", "feather", "stata"]


def init():
    output_format_help = ""
    for k, v in OUTPUT_FORMAT_DESC.items():
        output_format_help += "    {:6s}:{}\n".format(k, v)

    arg_parser = argparse.ArgumentParser(description="utility for CSV file",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:
  Process of '--serial_column' is done at first, so the result of '--serial_column' may be used as a coluumn for '--add_columns', others.
  Note: result of '--serial_column' will be affected at proceeding processing for '--drop_na_columns', others.

  All columns are read as "str", so you may convert type of those if need, using '--add_columns', '--trim_columns', '--type_columns'.

  For '--add_column', available name of column is to match with '[\w:;@_；：＠＿]+'.
  At '--add_columns', there are '$' prefix column names in right-side of each defitiion, see examples.

  At '--trim_columns', in right-side of each definition, there is a lambda function, 
  the function will be applied by Series.map, see examples.

  If you want to use commas in expression of '--add_columns' and '--trim_columns', the comma must be escaped by back-slash. see examples.
  For '--add_columns', values of each column, that start with '0b' or '0o' or '0x', are converted int integer internaly,
  but at output value of those columns was formatted back into original format.

  [DEPRECATE] '--change_timefreq' was deprecated. use 'csv_trimtime'.
  For '--change_timefreq', available methods are floor, ceil,round. About format string, you may find answer in
  'datetime  Basic date and time types https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior'.
  About 'freqnecy', you may check the document in 
  'Time series / date functionality https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases'.
  If you want to use commas and colon in expression of '--change_timefreq', those must be escaped by back-slash. see examples.

  After other processings, '--trim_columns' are applied immediately before output.
  When '--drop_dulicated' was given, first row that has same values of columns will be remained.

  For '--decompose_bit_string', new columns are added, names of those has '_Bnnn' as suffix.
  NBITS means minimum number of columns for decomposed results.
  If values has prefix '0b', '0o','0x' or is string of decimal, then the values are decoded into binary string and decomposed.
  And value of elements is treated as bits pattern string. So results have reversed order: 
   ex: COL_A:10011 => [COL_A_B000:"1",COL_A_B001:"1",COL_A_B002:"0",COL_A_B003:"0",COL_A_B004:"1"]
  Note: if there are "100" and "200" in the same column, "100" is treated as binary string "0b100", 
        but "200" is treated as decimal value and results is ["1","1","0","0","1","0","0","0"].

  For '--stack', there are [<column name>,'category','stacked_result'] as columns in header of results. 
  '<column name>' is name given by '--stack'.

  For '--fillna', if '@interpolate' was used as value, NaN are filled by interpolated by linear method with both inside and outside.
  If '@forward' was used as value, propagate last valid observation forward to next valid
  If '@backward' was used as value, use next valid observation to fill gap.

  For '--replace', definition has json format as dict: '{"old_value":"new_value",...}' 
  NOTE: In definition, old value must be string. ex: '{"1":"A"}'
  If you want to use commas in definition of '--replace', those must be escaped by back-slash. see examples.

  If you want to use commas and colon in expression of '--split_into_rows' and '--split_into_columns', 
  those must be escaped by back-slash. see examples.

  For '--split_into_columns', the separactor is sigle character or regexp.
  If named parameter is used, the names are names of columns in the result. see example.

  output format:
    csv      : comma-separated values (csv) file
    hdf      : HDF5 file using HDFStore
    parquet  : the binary parquet format, that reuires pyarrow module
    pickeld  : Pickle (serialize) object to file
    json     : JSON string
    feather  : binary Feather format, that requires pyarrow module
    stata    : Stata dta format

  processing order:
   add serial column, dropping columns(regx), dropping rows, dropping na, dropping duplicated, adding columns that was changed with time frequency, 
   adding columns, triming columns, type columns,filling value for na, replace values, split into rows, split into columns, 
   decompose bits string, sort/sort by datetime, rename columns, stacking

SECURITY WARNING:
  this use 'exec' for '--add_columns' and '--prologe', '--trim_columns' without any sanity.

example:
  csv_uty.py --serial_column=serial:100 test1.csv
  csv_uty.py --drop_columns=A,B --drop_rows=1 test1.csv
  csv_uty.py --drop_na_columns=all test1.csv | csv_uty.py --serial_column=serial:100 -
  csv_uty.py --drop_rows=0-1 test1.csv
  csv_uty.py --drop_na_columns=P1C1,P1C2,P2C1 test3.csv
  csv_uty.py --drop_duplicated=P1C1 test3.csv

  csv_uty.py --add_columns='NCOL1="PAT001",NCOL2=12345,NCOL3=${A}+${B}' test1.csv
  csv_uty.py --add_column='E=(${D}.fillna("0").apply(lambda x: int(x\,2)) & 0b10)' test1.csv
  acol='NCOL1="PAT001",NCOL2=12345,NCOL3=(${D}.fillna("0").apply(lambda x: int(x\,0)) & 0b10)!=0'
  csv_uty.py --add_columns="${acol}" test1.csv
  acol='NCOL1="PAT001",NCOL2=12345,NCOL3=np.sin(${A}.fillna("0").astype(float))'
  csv_uty.py --prologe='import numpy as np;' --add_columns="${acol}" --columns=NCOL1,NCOL2,NCOL3,A,B,C,D test1.csv
  acol='NCOL1=${A}.map(lambda x: format(int(x)\, "#010x")\, na_action="ignore")'
  csv_uty.py --prologe='import numpy as np;' --add_columns="${acol}" --columns=NCOL1,A,B,C,D test1.csv
  # Series  pandas 1.1.3 documentation https://pandas.pydata.org/pandas-docs/stable/reference/series.html#accessors
  csv_uty.py --add_columns='D=${ABC002}.str.replace(r":\d+$"\,":00"\,regex=True)' big_sample_headers.csv |\\
                                                              csv_plot_histogram.py --output=test.html --animation_column=D - ABC005
  csv_uty.py --add_columns='D=pd.to_datetime(${ABC002}\,format="%Y-%m-%d %H:%M:%S")' big_sample_headers.csv
  csv_uty.py --add_columns='D=pd.to_datetime(${ABC002}\,format="%Y-%m-%d %H:%M:%S"),E=${D}.dt.floor("30s")' big_sample_headers.csv |\\
                                                              csv_plot_histogram.py --animation_column=E --output=test.html - ABC005

  # the same as above
  #[DEPRECATE] '--change_timefreq' was deprecated. use 'csv_trimtime'.
  csv_uty.py --change_timefreq='D=ABC002:%Y-%m-%d %H\:%M\:%S:floor:30s' big_sample_headers.csv |\\
                                                              csv_plot_histogram.py --animation_column=D --output=test.html - ABC005

  csv_uty.py --trim_columns=D="lambda x: int(x\,0)" test1.csv # convert binary string into decimal value.
  csv_uty.py --type_columns=A=float,B=bin test2.csv

  csv_uty.py --decompose_bit_string=D:16 test1.csv |csvlook -I
  csv_uty.py --decompose_bit_string=A,B,C,D --rename_columns=A_B000:BIT_A,A_B001:BIT_B test1.csv

  csv_uty.py --rename_columns=A:abc,B:def test1.csv

  csv_uty.py --stack=ABC002 bit-pattern-headers.csv

  csv_uty.py --fillna=A=1,B=2,C="A B" test1.csv
  csv_uty.py --fillna=B=@interpolate test1.csv
  csv_uty.py --fillna=A=@forward t1.csv
  csv_uty.py --fillna=A=@backward t1.csv

  csv_uty.py --replace='A={"1":"A"\,"2":"B"},D={"a":1\,"b":0}' t1.csv

  csv_uty.py --split_into_rows="COL003" test_explode.csv
  csv_uty.py --split_into_rows="COL002:\:,COL003" test_explode.csv
  csv_uty.py --split_into_rows="COL002:\:" test_explode.csv |csvlook -I
  | COL001 | COL002 | COL003 | COL004   |
  | ------ | ------ | ------ | -------- |
  | A      | 1      | 1,2,3  | F1|F2|F3 |
  | A      | 2      | 1,2,3  | F1|F2|F3 |
  | A      | 3      | 1,2,3  | F1|F2|F3 |
  | B      | 2      | 4,5,6  | F2       |
  | C      | 3      | 7,8,9  | F1|F3    |

  csv_uty.py --split_into_columns="COL002:\:,COL004" test_explode.csv|csvlook -I
  | COL001 | COL002 | COL003 | COL004   | 1 | 2 | 3 | F1 | F2 | F3 |
  | ------ | ------ | ------ | -------- | - | - | - | -- | -- | -- |
  | A      | 1:2:3  | 1,2,3  | F1|F2|F3 | 1 | 1 | 1 | 1  | 1  | 1  |
  | B      | 2      | 4,5,6  | F2       | 0 | 1 | 0 | 0  | 1  | 0  |
  | C      | 3      | 7,8,9  | F1|F3    | 0 | 0 | 1 | 1  | 0  | 1  |

  csv_uty.py --split_into_columns="COL002:(?P<alpha>\w+)(?P<D>\d+),COL004" test_explode.csv|csvlook -I
  | COL001 | COL002 | COL003 | COL004   | alpha | D | F1 | F2 | F3 |
  | ------ | ------ | ------ | -------- | ----- | - | -- | -- | -- |
  | A      | 1:2:3  | 1,2,3  | F1|F2|F3 |       |   | 1  | 1  | 1  |
  | B      | AB2    | 4,5,6  | F2       | AB    | 2 | 0  | 1  | 0  |
  | C      | D3     | 7,8,9  | F1|F3    | D     | 3 | 1  | 0  | 1  |

  # in following example, column 'D' will be created as column of timestamp, and by those dataframe will be made into group and stacked.
  # at plot, the timestamp column 'D' will be used as animation key frames.
  # [DEPRECATE] '--change_timefreq' was deprecated. use 'csv_trimtime'.
  csv_uty.py --change_timefreq='D=ABC002:%Y-%m-%d %H\:%M\:%S:floor:10s' bit-pattern-headers.csv|\\
     csv_status.py --mode sum --group D -|csv_uty.py --drop_columns=ABC000,ABC001 - |\\
     csv_uty.py --stack=D - |csv_plot_bar.py --output=bit-pattern-headers_10sec_sum.html --animation_column=D --yrange=0,1 - category stacked_result

  csv_uty.py --sort=ABC004 test_sort.csv
  csv_uty.py --sort="desc|ABC004,ABC005" test_sort.csv
  csv_uty.py --sort_datetime="ABC002" test_sort.csv
  csv_uty.py --sort_datetime="desc|ABC002" test_sort.csv
  csv_uty.py --sort_datetime="ABC002:%Y-%m-%d %H\:%M\:%S" test_sort.csv

  csv_uty.py --output_format=hdf --output=test.dat bit-pattern-headers.csv

  input: test1.csv
  A,B,C,D
  1,2,3,0b01010
  4,5,6,0b01

  input: test3.csv
  P1C1,P1C2,P2C1,P2C2,N
  1,0,1,0,A
  1,0,0,1,B
  1,0,1,0,C
  1,0,1,0,D
  ,1,1,1,E
  ,,1,1,F
  1,1,,1,G


'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument("--serial_column",
                            dest="SERICOLUMN",
                            help="add new column that has continus numbers, 0-base. If STEP was given, steped number is used.",
                            type=str,
                            metavar='COLUMN[:STEP]',
                            default=None)
    arg_parser.add_argument("--drop_columns_regex",
                            dest="DCOLS_REGEX",
                            help="pattern of column names to drop",
                            type=str,
                            metavar='REGEX',
                            default=None)
    arg_parser.add_argument("--drop_columns",
                            dest="DCOLS",
                            help="names of columns to drop",
                            type=str,
                            metavar='COLUMN[,COLUMN[,COLUMN...]',
                            default=None)
    arg_parser.add_argument("--drop_rows",
                            dest="DROWS",
                            help="index of rows to drop, 0-base",
                            type=str,
                            metavar='INT[,INT]|INT-INT',
                            default=None)
    arg_parser.add_argument("--drop_na_columns",
                            dest="DNACOLS",
                            help="names of columns to check NA and to drop. if 'all', rows are dropped with how='any'",
                            type=str,
                            metavar='COLUMN[,COLUMN[,COLUMN...]',
                            default=None)
    arg_parser.add_argument(
        "--drop_duplicated",
        dest="DDUPCOLS",
        help="names of columns to check duplicated rows and to drop others than first. if 'all', all columns are used to check",
        type=str,
        metavar='COLUMN[,COLUMN[,COLUMN...]',
        default=None)
    arg_parser.add_argument("--prologe",
                            dest="PROLOGE",
                            help="pieces of python code to pre-load, for use in expression of '--add_columns'.",
                            type=str,
                            metavar='CODE;[CODE;CODE;...]',
                            default=None)
    arg_parser.add_argument(
        "--change_timefreq",
        dest="CHTFREQ",
        help="[DEPRECATED]change datetime frequeny unit: format of definitoin is 'new_column_name=old_col_name:format:method:frequency'."
        + " if you use comma or colon in expression, those must be escaped with back-slash",
        type=str,
        metavar='COLUMN=definition[,COLUMN=definition...]',
        default=None)
    arg_parser.add_argument("--add_columns",
                            dest="ACOLS",
                            help="names and expressions of columns to add or replace, with csv format." +
                            " if you use comma in expression, the comma must be escaped with back-slash",
                            type=str,
                            metavar='COLUMN=expr[,COLUMN=expr...]',
                            default=None)
    arg_parser.add_argument("--trim_columns",
                            dest="TRMS",
                            help="piece of python code for each column to replace and output",
                            type=str,
                            metavar='COLUMN=CODE[,COLUMN=CODE[,COLUMN=CODE...]',
                            default=None)
    arg_parser.add_argument("--type_columns",
                            dest="DTYPE",
                            help="data type for each column:type=str, int, float, bin, oct, hex",
                            type=str,
                            metavar='COLUMN=type[,COLUMN=type..]',
                            default=None)
    arg_parser.add_argument("--fillna",
                            dest="FILLNA",
                            help="fill na for each column. if starts with '@', internal function will be used, see remark.",
                            type=str,
                            metavar='COLUMN=value[,COLUMN=value...]',
                            default=None)
    arg_parser.add_argument("--replace",
                            dest="REPLACE",
                            help="replace value for each column",
                            type=str,
                            metavar='COLUMN=JSON[,COLUMN=JSON...]',
                            default=None)
    arg_parser.add_argument("--split_into_rows",
                            dest="SPLIT_CSV",
                            help="split each element value with csv format and store those into rows, default of separator=','",
                            type=str,
                            metavar='COLUMN[:SEPARATOR[,COLUMN:SEPARATOR]]',
                            default=None)
    arg_parser.add_argument("--split_into_columns",
                            dest="SPLIT_FLAG",
                            help="split each element value with flag format and store those into columns, default of separator='|'",
                            type=str,
                            metavar='COLUMN[:SEPARATOR[,COLUMN:SEPARATOR]]',
                            default=None)
    arg_parser.add_argument("--decompose_bit_string",
                            dest="DBIT",
                            help="decompose string as bit pattern. ex 01010101",
                            type=str,
                            metavar='COLUMN[:NBITS[,COLUMN...]]',
                            default=None)
    arg_parser.add_argument("--rename_columns",
                            dest="RENAMECOLS",
                            help="rename columns",
                            type=str,
                            metavar='OLD_NAME:NEW_NAME[,OLD_NAME:NEW_NAME...]',
                            default=None)
    arg_parser.add_argument("--sort",
                            dest="SORT",
                            help="sorting for columns, sort_order=ascendig or descendig",
                            type=str,
                            metavar="[sort_order|]COLUMN[,COLUMN...]",
                            default=None)
    arg_parser.add_argument("--sort_datetime",
                            dest="DTSORT",
                            help="sorting for columns as datetime, sort_order=ascendig or descendig",
                            type=str,
                            metavar="[sort_order|]COLUMN:FORMAT",
                            default=None)
    arg_parser.add_argument("--stack",
                            dest="STACKGCOL",
                            help="name of column to make group with stacking",
                            type=str,
                            metavar='COLUMN',
                            default=None)
    arg_parser.add_argument("--transpose", dest="TRANS", help="transpose dataframe", action="store_true", default=False)

    arg_parser.add_argument("--output_format", dest="OFORMAT", help="output format", choices=OUTPUT_FORMAT, default="csv")
    arg_parser.add_argument("--columns_regex",
                            dest="OCOLS_REGEX",
                            help="pattern of column names to output",
                            type=str,
                            metavar='COLUMN[,COLUMN[,COLUMN...]',
                            default=None)
    arg_parser.add_argument("--columns",
                            dest="OCOLS",
                            help="names of columns to output",
                            type=str,
                            metavar='COLUMN[,COLUMN[,COLUMN...]',
                            default=None)

    arg_parser.add_argument("--output",
                            dest="OUTPUT",
                            help="path of output csv file, default=stdout",
                            type=str,
                            metavar='FILE',
                            default=sys.stdout)

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='file to read. if "-", stdin is used')
    # arg_parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    # arg_parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    args = arg_parser.parse_args()
    return args


def get_output_file(outname_func, input_file, output_file, buffered=False):
    """retriev path of output file from path of 'input file'.
       if 'output_file' was defined, then the value will be returned.
       if 'output_file' was not defined, then 'output_file' will be derived from 'input_file'.

    :param outname_func: function to make output file name, function has path of input file as only one argument.
    :param input_file: path of input file
    :param output_file: path of output file
    :param buffered: if True and input_file=="-", then sys.stdout.buffer as output_file will be returned.
                     if False, sys.stdout will be returned.
    :returns: path of output file or sys.stdout[.buffer]
    :rtype: str or file handler

    :exmple:
          output_file = get_output_file(lambda x: Path(x).stem + "_test.csv", input_file, output_file)


    """
    # output_file = Path(input_file).stem + "_hist.csv"
    if output_file is None or len(output_file) == 0:
        if isinstance(input_file, str) and input_file != "-":
            output_file = outname_func(input_file)
        else:
            if buffered:
                output_file = sys.stdout.buffer
            else:
                output_file = sys.stdout
    elif isinstance(output_file, str) and output_file == "-":
        if buffered:
            output_file = sys.stdout.buffer
        else:
            output_file = sys.stdout

    if input_file == "-":
        input_file = sys.stdin

    return output_file


def trim_output_file(output_file, mkdir=True, overwrite=True):
    """check path of output file

    :param output_file: path of output file
    :param mkdir: if True, do mkdir
    :param overwrite: if False and file existed, then exception will be raised.

    """
    if isinstance(output_file, str):
        p_dir = Path(output_file).parent
        if mkdir and not Path(p_dir).exists():
            Path(p_dir).mkdir(exist_ok=True, parents=True)

        if not overwrite and Path(output_file).exists():
            raise Exception("{} already exists".format(output_file))


def type_columns_in_df(df, typ_columns):
    """ set type of columns at output results

    :param df: dataframe that will be modified inplace
    :param type_columns: list of definitions

    """
    print("%inf:csv_uty:type_columns:{}".format(typ_columns), file=sys.stderr)
    for fc in typ_columns:
        cs = re.split(r"\s*=\s*", fc, maxsplit=1)
        if len(cs) >= 2:
            typ = cs[1]
            if cs[0] in df.columns:
                try:
                    if typ == "bin":
                        df[cs[0]] = df[cs[0]].astype(str, errors="ignore")
                        # print(df[cs[0]].dtype)
                        df[cs[0]] = df[cs[0]].apply(lambda x: ("0b{:016b}".format(int(x, 0)) if x != "nan" else x))
                    elif typ == "oct":
                        df[cs[0]] = df[cs[0]].astype(str, errors="ignore")
                        df[cs[0]] = df[cs[0]].apply(lambda x: ("0b{:016o}".format(int(x, 0)) if x != "nan" else x))
                    elif typ == "hex":
                        df[cs[0]] = df[cs[0]].astype(str, errors="ignore")
                        df[cs[0]] = df[cs[0]].apply(lambda x: ("0b{:016x}".format(int(x, 0)) if x != "nan" else x))
                    else:
                        df[cs[0]] = df[cs[0]].astype(cs[1])
                except ValueError as e:
                    print("??Error:csv_uty:type_columns_in_df:{}={}:{}".format(cs[0], cs[1], e), file=sys.stderr)
                except TypeError as e:
                    print("??Error:csv_uty:type_columns_in_df:{}={}:{}".format(cs[0], cs[1], e), file=sys.stderr)
        else:
            print("#warning:csv_uty:type_columns: invalid definitin for type columns:{}".format(fc), file=sys.stderr)


def trim_columns_in_df(df, fmt_columns):
    """ trim output results for each column

    :param df: dataframe that will be modified inplace
    :param fmt_columns: list of definitions

    """
    print("%inf:csv_uty:trim_columns:{}".format(fmt_columns), file=sys.stderr)
    for fc in fmt_columns:
        cs = re.split(r"\s*=\s*", fc, maxsplit=1)
        if len(cs) >= 2:
            if cs[0] in df.columns:
                cs[1] = re.sub(r'\\,', r',', cs[1])
                try:
                    estr = 'df["{0}"] = df["{0}"].map({1}, na_action="ignore")'.format(cs[0], cs[1])
                    print("%Inf:csv_uty:trim columns:{}".format(estr), file=sys.stderr)
                    exec(estr)
                except ValueError as e:
                    print("??Error:csv_uty:trim_columns_in_df:{}={}:{}".format(cs[0], cs[1], e), file=sys.stderr)
        else:
            print("#warning:csv_uty:trim_columns: invalid definitin for triming columns:{}".format(fc), file=sys.stderr)


def add_columns_to_df(df, add_columns):
    """add or replace columns as result of evaluating expression

    :param df: dataframe that will be modified inplace.
    :param add_columns: list of defitions

    """

    print("%inf:csv_uty:add_columns:{}".format(add_columns), file=sys.stderr)
    for ac in add_columns:
        cs = re.split(r"\s*=\s*", ac, maxsplit=1)
        if len(cs) >= 2:
            # if cs[0] in df.columns:
            #     print("??Error:csv_uty:add_columns:{} was already exists".format(cs[0]), file=sys.stderr)
            #     exit(1)
            rcs = cs[1]
            # rcs = re.sub(r'\$(\w+)', r'df["\1"]', rcs)
            # rcs = re.sub(r'\$([\w:;@_；：＠＿\(\)（）]+)', r'df["\1"]', rcs)
            rcs = re.sub(r'\${([^}]+)}', r'df["\1"]', rcs)
            rcs = re.sub(r'(0b[01]+|0o[0-7]+|0x[0-9a-f]+)', lambda m: str(int(m.group(1), 0)), rcs, re.IGNORECASE)
            rcs = re.sub(r'\\,', r',', rcs)
            try:
                estr = 'df["{}"]={}'.format(cs[0], rcs)
                print("%Inf:csv_uty:add columns:{}".format(estr), file=sys.stderr)
                exec(estr)
            except TypeError as e:
                print("??Error:csv_uty:add_columns_to_df:{}={}:{}".format(cs[0], rcs, e), file=sys.stderr)

        else:
            print("#warning:csv_uty:add_columns: invalid definitin for add columns:{}".format(ac), file=sys.stderr)


def prefix_number_to_int(df):
    """convert prefixed integer in dataframe into integer

    :param df: dataframe that will be modified inplace.
    :returns: information of modified columns
    :rtype: list of dict

    """
    done_columns = []
    for col in df.columns:
        val = str(df[col][0])
        if re.match(r'^(0x[a-f0-9]|0o[0-7]+|0b[01]+)$', val, re.IGNORECASE) is not None:
            df[col] = df[col].map(lambda x: int(x, 0), na_action='ignore')
            done_columns.append({"column": col, "mode": val[:2], "length": len(val) - 2})
    return done_columns


def int_to_prefix_numer(df, done_columns):
    """convert integer in dataframe into formatted string

    :param df: dataframe that will be modified inplace
    :param done_columns: result from prefix_number_to_int

    """
    for col_d in done_columns:
        col = col_d["column"]
        mode = col_d["mode"]
        slen = col_d["length"]
        fmt = "#0{}{}".format(slen + 2, mode[1])
        df[col] = df[col].map(lambda x: format(int(x), fmt), na_action='ignore')


def parse_drop_rows(d_rows):
    """parse defitions about dorpping rows

    :param d_rows: list of definitions
    :returns: list of rows
    :rtype: list[int]

    """
    result = []
    for dr in d_rows:
        if re.search(r"-", dr) is not None:
            csv = dr.split("-")
            result.extend(range(int(csv[0]), int(csv[1]) + 1))
        else:
            result.append(dr)

    result = list(map(int, result))

    return result


def decomp_bits_pattern(df, column_name, nbits=0):
    """decompose string into character as bits pattern.

    :param df: DataFrame
    :param column_name: name of column
    :returns: DataFrame
    :rtype: 
    :remark:
       If possible, value will be translated into integer and converted into binary pattern.
       In case of failure, columns are filled by '0'.
       If there was quatation, they is removed.
       If there are "100" and "200" in the same column, "100" is treated as binary string "0b100", 
        but "200" is treated as decimal value and results is ["1","1","0","0","1","0","0","0"].

    """
    print("%inf:csv_uty:decomp_bits:{}".format(column_name), file=sys.stderr)
    df.reset_index(inplace=True)
    ds = df[column_name]
    if ds.dtype != np.dtype('str') and ds.dtype != np.dtype('object'):
        print("??Error:csv_uty:{} has no string.".format(column_name), file=sys.stderr)
        return
    if nbits > 0:
        cns = ["{}_B{:03d}".format(column_name, i) for i in range(nbits)]
        df[cns] = 0
        cnames = set(cns)
    else:
        cnames = set()
    for ir in range(len(df)):
        val = ds.loc[ir]
        if val is np.nan or val is None:
            continue
        val = val.strip('"\'')  # removing quotation
        val = re.sub(r"\.0$", "", val)  # removing the trailing ".0"
        if not val.isdecimal() and not (val.startswith("0b") or val.startswith("0o") or val.startswith("0x") and val[2:].isdecimal()):
            print("??Error:csv_uty:{} was not decimal value:{}".format(val, column_name), file=sys.stderr)
            continue
        val = val.lower()
        if val.isdecimal() and len(re.sub(r"[01]", "", val)) > 0:
            val = "{:0b}".format(int(val))
        elif val.startswith("0b"):
            val = "{:0b}".format(int(val[2:], 2))
        elif val.startswith("0o"):
            val = "{:0b}".format(int(val[2:], 8))
        elif val.startswith("0x"):
            val = "{:0b}".format(int(val[2:], 16))
        vals = list(reversed(list(val)))
        vname = ["{}_B{:03d}".format(column_name, i) for i in range(len(vals))]
        cnames.update(set(vname))
        df.loc[ir, vname] = vals

    print("%Inf:csv_uty:new columns was added: {}".format(sorted(list(cnames))), file=sys.stderr)

    # fillna by '0'
    for cn in cnames:
        df[cn].fillna(0, inplace=True)
        df[cn] = df[cn].astype('int64')

    return df


def change_time_frequency(df, ch_definitions):
    """FIXME! briefly describe function

    :param df: 
    :param ch_definitions: [new_column_name=old_column:format:method:frequency,...]
    :returns: 
    :rtype: 

    """
    print("%inf:csv_uty:change_timefreq:{}".format(ch_definitions), file=sys.stderr)
    print("#warn:csv_uty:change_timefreq:THIS IS DEPRECATED. USE csv_trimtime.py", file=sys.stderr)

    try:
        for cdf in ch_definitions:
            cvs = re.split(r"\s*(?<!\\)=\s*", cdf)
            cname = cvs[0]
            if len(cvs) < 2:
                print("??error:csv_uty:change_timefreq:invalid format of definition:{}".format(cdf), file=sys.stderr)
                sys.exit(1)
            cvs = re.split(r"\s*(?<!\\):\s*", cvs[1])
            if len(cvs) < 3:
                print("??error:csv_uty:change_timefreq:invalid format of definition:{}".format(cdf), file=sys.stderr)
                sys.exit(1)
            t_col = cvs[0]
            t_format = cvs[1]
            t_method = cvs[2]
            t_freq = cvs[3]
            t_format = re.sub(r"\\:", ":", t_format)
            t_format = re.sub(r"\\=", "=", t_format)
            df[cname] = pd.to_datetime(df[t_col], format=t_format)
            if t_method == "floor":
                df[cname] = df[cname].dt.floor(t_freq).dt.strftime(t_format)
            elif t_method == "ceil":
                df[cname] = df[cname].dt.ceil(t_freq).dt.strftime(t_format)
            elif t_method == "round":
                df[cname] = df[cname].dt.round(t_freq).dt.strftime(t_format)
            else:
                print("#warn:csv_uty:invalid method for '--change_timefreq':{} in {}".format(t_method, cdf), file=sys.stderr)
                continue
            vcs = df[cname].value_counts()
            print("%inf:csv_uty:change_timefreq:column={}:number of uniq periods={}:max count in each period={}".format(
                cname, len(vcs), max(vcs)),
                  file=sys.stderr)
    except ValueError as e:
        print("??error:csv_uty:change time frequency:{}:{}".format(t_col, e), file=sys.stderr)
        sys.exit(1)

    return df


def do_fillna(df, fillna_defs):
    """FIXME! briefly describe function

    :param df: 
    :param fillna_defs: [COLUMN=[@]value,...]
    :returns: 
    :rtype: 

    """
    print("%inf:csv_uty:fillna:{}".format(fillna_defs), file=sys.stderr)
    for fd in fillna_defs:
        cvs = re.split(r"\s*(?<!\\)=\s*", fd)
        cname = cvs[0]
        f_value = cvs[1]
        if f_value == "@interpolate":
            df[cname] = df[cname].astype('float64', errors='ignore')
            df[cname].interpolate(limit_area='inside', inplace=True)
            df[cname].interpolate(limit_area='outside', inplace=True)
        elif f_value == "@forward":
            df[cname].ffill(inplace=True)
        elif f_value == "@backward":
            df[cname].bfill(inplace=True)
        else:
            df[cname].fillna(f_value, axis=0, inplace=True)

    return df


def do_replace(df, replace_defs):
    """FIXME! briefly describe function

    :param df: 
    :param replace_defs: [COLUMN=JSON,...]
    :returns: 
    :rtype: 

    """
    print("%inf:csv_uty:replace:{}".format(replace_defs), file=sys.stderr)
    for fd in replace_defs:
        cvs = re.split(r"\s*(?<!\\)=\s*", fd)
        cname = cvs[0]
        r_value = cvs[1]
        r_value = re.sub(r"\\,", ",", r_value)
        rep_def = json.loads(r_value)
        df[cname].replace(rep_def, inplace=True)

    return df


def do_split_into_rows(df, split_csvs):
    """FIXME! briefly describe function

    :param df: 
    :param split_csvs: [COLUMN[:SEPARATOR],...]
    :returns: 
    :rtype: 

    """
    print("%inf:csv_uty:split_into_rows:{}".format(split_csvs), file=sys.stderr)
    for sc in split_csvs:
        cvs = re.split(r"\s*(?<!\\):\s*", sc)
        cname = cvs[0]
        if len(cvs) > 1:
            sep = cvs[1].lstrip("\\")
        else:
            sep = ","
        if len(sep) == 0:
            print("??error:csv_uty:invalid separator:'{}'".format(sep), file=sys.stderr)
            sys.exit(1)
        df[cname] = df[cname].str.split(sep)
        df = df.explode(cname)

    return df


def do_split_into_columns(df, split_flags):
    """FIXME! briefly describe function

    :param df: 
    :param split_flags: [COLUMN[:SEPARATOR],...]]
                        if length of SEPARATOR, it is treadted as regexp.
    :returns: 
    :rtype: 

    """
    print("%inf:csv_uty:split_into_columns:{}".format(split_flags), file=sys.stderr)
    for sf in split_flags:
        cvs = re.split(r"\s*(?<!\\):\s*", sf)
        cname = cvs[0]
        if len(cvs) > 1:
            sep = cvs[1].lstrip("\\")
        else:
            sep = "|"
        if len(sep) == 0:
            print("??error:csv_uty:invalid separator:'{}'".format(sep), file=sys.stderr)
            sys.exit(1)
        if len(sep) > 1:
            res_df = df[cname].str.extract(sep, expand=True)
        else:
            res_df = df[cname].str.get_dummies(sep=sep)
        df = pd.concat([df, res_df], axis=1)

    return df


def do_sort(df, column_defs, datetime_fmt=None):
    if datetime_fmt is None:
        print("%inf:csv_uty:sort:{}".format(column_defs), file=sys.stderr)
    else:
        print("%inf:csv_uty:sort as datetime:{},fmt={}".format(column_defs, datetime_fmt), file=sys.stderr)
    # column_defs= [asc_or_desc|]column[,column...]

    ascending = True
    if column_defs.find("|") != -1:
        cvs = re.split(r"\|", column_defs)
        if cvs[0].lower().startswith("asc"):
            ascending = True
        elif cvs[0].lower().startswith("desc"):
            ascending = False
        else:
            print("#warn:csv_uty:sort:invalid sort order:{}, ascending is assumed".format(cvs[0]), file=sys.stderr)

        column_defs = cvs[1]

    columns = re.split(r"\s*,\s*", column_defs)

    if datetime_fmt is not None:
        for cn in columns:
            df[cn] = pd.to_datetime(df[cn], format=datetime_fmt)

    df.sort_values(columns, ascending=ascending, inplace=True, axis=0, na_position="last")
    return df


def output_dataframe(df, output_file, output_format, index=False, columns=[]):
    """FIXME! briefly describe function

    :param df: 
    :param output_file: 
    :param output_format: 
    :param index: 
    :param columns: 
    :returns: 
    :rtype: 

    """
    print("%inf:csv_uty:output into:{} with '{}' format".format(output_file, output_format), file=sys.stderr)
    if len(columns) > 0:
        d_cols = list(set(df.columns) - set(columns))
        df.drop(columns=d_cols, inplace=True)
    if output_format == "csv":
        df.to_csv(output_file, index=index)
    elif output_format == "hdf":
        df.to_hdf(output_file, key="csv_uty", mode="w", complevel=6)
    elif output_format == "parquet":
        df.to_parquet(output_file, index=index)
    elif output_format == "pickel":
        df.to_pickle(output_file)
    elif output_format == "json":
        df.to_json(output_file)
    elif output_format == "feather":
        df.to_feather(output_file)
    elif output_format == "stata":
        df.to_stata(output_file, write_index=index)


# def do_join_columns(df):
#     df[cname] = df[columns].agg(sep.join, axis=1)
#     pass

if __name__ == "__main__":
    args = init()
    csv_file = args.csv_file
    output_file = args.OUTPUT
    trans_mode = args.TRANS
    prologe = args.PROLOGE
    output_format = args.OFORMAT

    if output_format in OUTPUT_REQUIRED_FILE and output_file == sys.stdout:
        print("??error:csv_uty:'--output' was required fot format:{}".format(output_format), file=sys.stderr)
        sys.exit(1)

    if prologe is not None:
        pps = re.split(r'\s*;\s*', prologe)
        for pp in pps:
            if len(pp) == 0:
                continue
            print("%Inf:csv_uty:exec python code:{}".format(pp), file=sys.stderr)
            exec(pp)

    output_columns_s = args.OCOLS
    output_columns = []
    if output_columns_s is not None:
        output_columns = re.split(r"\s*,\s*", output_columns_s)

    output_columns_regex = args.OCOLS_REGEX

    # sorting
    sort_defs = args.SORT
    dt_sort_defs = args.DTSORT
    dt_sort_fmt = None
    if sort_defs is not None and dt_sort_defs is not None:
        print("??error:csv_uty:invalid combination between '--sort' and '--sort_datetime'", file=sys.stderr)
        sys.exit(1)
    if dt_sort_defs is not None:
        cvs = re.split(r"(?<!\\):", dt_sort_defs)
        if len(cvs) > 1:
            dt_sort_fmt = cvs[1]
            dt_sort_fmt = re.sub(r"\\", "", dt_sort_fmt)
        else:
            dt_sort_fmt = "%Y-%m-%d %H:%M:%S"
        sort_defs = cvs[0]

    # time frequency
    ch_timefreqs_s = args.CHTFREQ
    ch_timefreqs = []
    if ch_timefreqs_s is not None:
        ch_timefreqs = re.split(r"\s*(?<!\\),\s*", ch_timefreqs_s)

    # fillna
    fillna_defs_s = args.FILLNA
    fillna_defs = []
    if fillna_defs_s is not None:
        fillna_defs = re.split(r"\s*(?<!\\),\s*", fillna_defs_s)

    # replace
    replace_defs_s = args.REPLACE
    replace_defs = []
    if replace_defs_s is not None:
        replace_defs = re.split(r"\s*(?<!\\),\s*", replace_defs_s)

    # split csv
    split_csvs_s = args.SPLIT_CSV
    split_csvs = []
    if split_csvs_s is not None:
        split_csvs = re.split(r"\s*(?<!\\),\s*", split_csvs_s)

    # split flag
    split_flags_s = args.SPLIT_FLAG
    split_flags = []
    if split_flags_s is not None:
        split_flags = re.split(r"\s*(?<!\\),\s*", split_flags_s)

    # decompose string
    decomp_bits_column_s = args.DBIT
    decomp_bits_columns = []
    if decomp_bits_column_s is not None:
        decomp_bits_columns = re.split(r"\s*,\s*", decomp_bits_column_s)

    # drop columns
    drop_columns_s = args.DCOLS
    drop_columns = []
    if drop_columns_s is not None:
        drop_columns = re.split(r"\s*,\s*", drop_columns_s)
        # print("%Inf:csv_uty:removed columns:{}".format(drop_columns), file=sys.stderr)
        for dc in drop_columns:
            if dc in output_columns:
                output_columns.remove(dc)
                print("#warning:csv_uty:{} was rmoved from output columns".format(dc), file=sys.stderr)

    # drop columns
    drop_columns_regex = args.DCOLS_REGEX

    # drop rows
    drop_rows_s = args.DROWS
    drop_rows = []
    if drop_rows_s is not None:
        drop_rows = re.split(r"\s*,\s*", drop_rows_s)
        print("%Inf:csv_uty:removed rows:{}".format(drop_rows), file=sys.stderr)

    # drop na
    drop_na_columns_s = args.DNACOLS
    drop_na_columns = []
    if drop_na_columns_s is not None:
        drop_na_columns = re.split(r"\s*,\s*", drop_na_columns_s)
        print("%Inf:csv_uty:check na and drop:{}".format(drop_na_columns), file=sys.stderr)

    # drop duplicated rows
    drop_dup_columns_s = args.DDUPCOLS
    drop_dup_columns = []
    if drop_dup_columns_s is not None:
        drop_dup_columns = re.split(r"\s*,\s*", drop_dup_columns_s)
        print("%Inf:csv_uty:check duplicated and drop:{}".format(drop_dup_columns), file=sys.stderr)

    # add columns
    add_columns_s = args.ACOLS
    add_columns = []
    if add_columns_s is not None:
        add_columns = re.split(r"\s*(?<!\\),\s*", add_columns_s)

    # trim columns
    trm_columns_s = args.TRMS
    trm_columns = []
    if trm_columns_s is not None:
        trm_columns = re.split(r"\s*(?<!\\),\s*", trm_columns_s)

    # type columns
    typ_columns_s = args.DTYPE
    typ_columns = []
    if typ_columns_s is not None:
        typ_columns = re.split(r"\s*(?<!\\),\s*", typ_columns_s)

    if csv_file == "-":
        in_file = sys.stdin
    else:
        in_file = csv_file

    serial_column_s = args.SERICOLUMN
    serial_column = ""
    if serial_column_s is not None:
        cvs = re.split(r"\s*:\s*", serial_column_s)
        serial_column = cvs[0]
        if len(cvs) > 1:
            serial_step = int(cvs[1])
        else:
            serial_step = 1

    rename_columns_s = args.RENAMECOLS
    rename_columns = {}
    if rename_columns_s is not None:
        cvs = re.split(r"\s*,\s*", rename_columns_s)
        for cs in cvs:
            cns = re.split(r"\s*:\s*", cs)
            if len(cns) < 2:
                print("#warn:csv_uty:invalid argument for rename columns:{}".format(cs), file=sys.stderr)
            else:
                rename_columns[cns[0]] = cns[1]

    stack_group_column = args.STACKGCOL
    if stack_group_column is not None and trans_mode:
        print("??error:csv_uty:invalid combination: '--stack' and '--transpose'", file=sys.stderr)
        sys.exit(1)

    #--- processig
    print("%Inf:csv_uty:read data from {}".format(in_file), file=sys.stderr)
    csv_df = pd.read_csv(in_file, dtype="string")
    # csv_df = pd.read_csv(in_file)

    # columsn to output
    if output_columns_regex is not None:
        o_cols = [v for v in csv_df.columns if re.search(output_columns_regex, v)]
        print("%inf:csv_uty:output_columns_regex:columns to output:{}".format(o_cols), file=sys.stderr)
        output_columns.extend(o_cols)

    # add serial column
    if len(serial_column) > 0:
        print("%Inf:csv_uty:add serial column:{}".format(serial_column), file=sys.stderr)
        if serial_column in csv_df:
            print("#Warn:csv_uty:{} already exits, it was overwritten.", file=sys.stderr)
        csv_df[serial_column] = list(range(0, len(csv_df) * serial_step - 1, serial_step))

    # drop columns
    if drop_columns_regex is not None:
        d_cols = [v for v in csv_df.columns if re.search(drop_columns_regex, v)]
        print("%inf:csv_uty:drop_columns_regex: columns to drop:{}".format(d_cols), file=sys.stderr)
        drop_columns.extend(d_cols)
        for dc in drop_columns:
            if dc in output_columns:
                output_columns.remove(dc)
                print("#warning:csv_uty:{} was rmoved from output columns by regex".format(dc), file=sys.stderr)

    # dropping columns
    if len(drop_columns) > 0:
        print("%Inf:csv_uty:drop columns:{}".format(drop_columns), file=sys.stderr)
        try:
            csv_df.drop(columns=drop_columns, inplace=True)
        except KeyError as e:
            print("??Error:csv_uty:invalid name of column in '--drop_columns':{} ".format(e), file=sys.stderr)
            sys.exit(1)

    # dropping rows
    if len(drop_rows) > 0:
        print("%Inf:csv_uty:drop rows:{}".format(drop_rows), file=sys.stderr)
        drop_rows = parse_drop_rows(drop_rows)
        try:
            csv_df.drop(index=csv_df.index[drop_rows], inplace=True)
        except IndexError as e:
            print("??Error:csv_uty:invalid index of row in '--drop_rows':{} ".format(e), file=sys.stderr)
            sys.exit(1)

    # dropping na
    if len(drop_na_columns) > 0:
        nr0 = len(csv_df)
        print("%Inf:csv_uty:drop na rows for {}".format(drop_na_columns), file=sys.stderr)
        if drop_na_columns[0] == "all":
            csv_df.dropna(how="any", axis="rows", inplace=True)
        else:
            try:
                csv_df.dropna(subset=drop_na_columns, axis="rows", inplace=True)
            except KeyError as e:
                print("??Error:csv_uty:invalid name of column in '--drop_na_columns':{} ".format(e), file=sys.stderr)
                sys.exit(1)
        print("%Inf:csv_uty:number of dropped rows as na: {}".format(nr0 - len(csv_df)), file=sys.stderr)

    # dropping duplicated
    if len(drop_dup_columns) > 0:
        nr0 = len(csv_df)
        print("%Inf:csv_uty:drop duplicated rows for {}".format(drop_dup_columns), file=sys.stderr)
        if drop_dup_columns[0] == "all":
            csv_df.drop_duplicates(keep="first", inplace=True)
        else:
            try:
                csv_df.drop_duplicates(subset=drop_dup_columns, keep="first", inplace=True)
            except KeyError as e:
                print("??Error:csv_uty:invalid name of column in '--drop_duplicated':{} ".format(e), file=sys.stderr)
                sys.exit(1)
        print("%Inf:csv_uty:number of dropped rows as duplicated: {}".format(nr0 - len(csv_df)), file=sys.stderr)

    try:
        # adding new columns for changing time frequency
        if len(ch_timefreqs) > 0:
            print("%Inf:csv_uty:changing time frequency", file=sys.stderr)
            csv_df = change_time_frequency(csv_df, ch_timefreqs)

        # adding columns
        if len(add_columns) > 0:
            print("%Inf:csv_uty:adding columns", file=sys.stderr)
            toint_columns = prefix_number_to_int(csv_df)
            add_columns_to_df(csv_df, add_columns)
            int_to_prefix_numer(csv_df, toint_columns)

        # triming columns
        if len(trm_columns) > 0:
            print("%Inf:csv_uty:trim column", file=sys.stderr)
            trim_columns_in_df(csv_df, trm_columns)

        # type columns
        if len(typ_columns) > 0:
            print("%Inf:csv_uty:set data type", file=sys.stderr)
            type_columns_in_df(csv_df, typ_columns)

    except NameError as e:
        print("??Error:csv_uty:you may use '--prologe' option: {}".format(e), file=sys.stderr)
        sys.exit(1)

    # fill na
    if len(fillna_defs) > 0:
        csv_df = do_fillna(csv_df, fillna_defs)

    # replace
    if len(replace_defs) > 0:
        csv_df = do_replace(csv_df, replace_defs)

    # split csv
    if len(split_csvs) > 0:
        csv_df = do_split_into_rows(csv_df, split_csvs)

    # split flag
    if len(split_flags) > 0:
        csv_df = do_split_into_columns(csv_df, split_flags)

    # decomposing bits string
    for decomp_bits_column in decomp_bits_columns:
        cvs = re.split(r":", decomp_bits_column)
        cn = cvs[0]
        print("%Inf:csv_uty:decompose bit pattern:{}".format(cn), file=sys.stderr)
        if len(cvs) > 1:
            nb = int(cvs[1])
        else:
            nb = 0
        csv_df = decomp_bits_pattern(csv_df, cn, nbits=nb)

    # sort
    if sort_defs is not None:
        csv_df = do_sort(csv_df, sort_defs, datetime_fmt=dt_sort_fmt)

    # rename columns
    if len(rename_columns) > 0:
        print("%Inf:csv_uty:rename columns:{}".format(rename_columns), file=sys.stderr)
        invalid_cols = list(set(rename_columns.keys()) - set(csv_df.columns))
        if len(invalid_cols) > 0:
            print("#warn:csv_uty: invalid columns in renaming:{}".format(invalid_cols), file=sys.stderr)
        csv_df.rename(columns=rename_columns, inplace=True, errors='ignore')

    if not all([v in csv_df.columns for v in output_columns]):
        print("??Error:csv_uty:'--columns' was inconsist for input", file=sys.stderr)
        sys.exit(1)

    if stack_group_column is not None:
        if len(output_columns) > 0:
            csv_df2 = csv_df[output_columns]
        else:
            csv_df2 = csv_df
        csv_df2.set_index(stack_group_column, inplace=True)
        csv_df2 = csv_df2.stack()
        csv_df2.name = "stacked_result"
        inames = list(csv_df2.index.names)
        inames[1] = "category"
        csv_df2.index.set_names(inames, inplace=True)
        # csv_df2.to_csv(output_file)
        output_dataframe(csv_df2, output_file, output_format, index=True)
    elif trans_mode:
        if len(output_columns) > 0:
            csv_df = csv_df[output_columns]
        csv_df = csv_df.T
        csv_df.index.name = "column"
        # csv_df.to_csv(output_file)
        output_dataframe(csv_df, output_file, output_format, index=True)
    else:
        # if len(output_columns) == 0:
        #     csv_df.to_csv(output_file, index=False)
        # else:
        #     csv_df.to_csv(output_file, index=False, columns=output_columns)
        output_dataframe(csv_df, output_file, output_format, index=False, columns=output_columns)
