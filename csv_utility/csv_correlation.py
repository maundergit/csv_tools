#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_correlation.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-11-12 18:37:04>
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
import statsmodels.tsa.api as tsa
import pandas as pd

VERSION = 1.0


def init():
    # argparse --- コマンドラインオプション、引数、サブコマンドのパーサー  Python 3.8.5 ドキュメント https://docs.python.org/ja/3/library/argparse.html
    arg_parser = argparse.ArgumentParser(description="evaluate cross/auto correlation between columns",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:
  In results, prefix 'ac_' means result of auto-correlation, prefix 'cc_' means result of cross-correlation.
  prefix 'ac_ci_l' and 'ac_cf_u' mean lower adn upper level of 95% confidence interval for no-correlation.

  For '--mode=cross', nlags means number of records in output. If you want all records from cross-correlation, set nlags=0.

example:
  csv_correlation.py test_correlation.csv COL_0000,COL_0001
  csv_correlation.py test_correlation.csv COL_0000|head|csvlook -I
| index | ac_COL_0000            | ac_ci_l_COL_0000     | ac_ci_u_COL_0000    |
| ----- | ---------------------- | -------------------- | ------------------- |
| 0     | 1.0                    | 1.0                  | 1.0                 |
| 1     | 0.07018334701195321    | -0.06840703542301456 | 0.20877372944692096 |
| 2     | -0.031686282848955645  | -0.17095764718861142 | 0.10758508149070015 |
| 3     | 0.06474599533914761    | -0.07466376744626992 | 0.20415575812456516 |
| 4     | -0.07187457627030945   | -0.21186070987120875 | 0.06811155733058984 |
| 5     | -0.0032344642148376297 | -0.14392762546855406 | 0.13745869703887878 |
| 6     | -0.02065593286982406   | -0.16135052234546393 | 0.12003865660581581 |
| 7     | 0.03586195035334148    | -0.10489087472112046 | 0.1766147754278034  |
| 8     | 0.05144023922871804    | -0.08948797647058224 | 0.19236845492801832 |

  csv_correlation.py --mode=cross test_correlation.csv COL_0000,COL_0001,COL_0002
  csv_correlation.py --mode=cross --sampling=2 test_correlation.csv COL_0000,COL_0001,COL_0002|head|csvlook -I
| index | cc_COL_0000_COL_0001  | cc_COL_0000_COL_0002  | cc_COL_0001_COL_0002  |
| ----- | --------------------- | --------------------- | --------------------- |
| 0     | -0.07832200979116527  | -0.0361744688777645   | -0.0383920692904824   |
| 1     | -0.0584437912103411   | 0.02924305243353182   | 0.0014283173939956392 |
| 2     | -0.004634262357976521 | 0.009863911035045745  | 0.0700311412765593    |
| 3     | 0.08549028836897214   | 0.145849764523322     | -0.07607057576313002  |
| 4     | 0.06411213630824009   | -0.009025766566690439 | -0.043516364265988865 |
| 5     | 0.053392718054984536  | -0.04056558651200204  | 0.09684720026396708   |
| 6     | -0.10900425075345083  | -0.022320478554022246 | 0.0459223360399405    |
| 7     | 0.014787564430673562  | -0.02152087172311092  | -0.00444335370431942  |
| 8     | -0.02779304465519147  | -0.027346286491568755 | 0.12710493528359032   |

'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument("--mode", dest="MODE", help="correlation mode", choices=["auto", "cross", "partial"], default="auto")
    arg_parser.add_argument("--nlags", dest="NLAGS", help="maximum number of lags,default=100", type=int, metavar='INT', default=100)
    arg_parser.add_argument("--sampling", dest="RSKIP", help="number of step for rows to do sample", type=int, metavar='INT', default=1)
    arg_parser.add_argument("--na_value",
                            dest="NAVALUE",
                            help="value to fill for NaN,default=0",
                            type=float,
                            metavar='FLOAT',
                            default=0.0)

    arg_parser.add_argument("--output",
                            dest="OUTPUT",
                            help="path of outut file, default=stdout",
                            type=str,
                            metavar='FILE',
                            default=sys.stdout)

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='files to read, if empty, stdin is used')
    arg_parser.add_argument('columns', metavar='COLUMN[,COLUMN...]', help='columns to do')

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    args = init()
    csv_file = args.csv_file
    output_file = args.OUTPUT

    mode = args.MODE
    nlags = args.NLAGS
    r_skip = args.RSKIP
    na_value = args.NAVALUE

    columns = re.split(r"\s*,\s*", args.columns)

    if mode == "cross" and len(columns) == 1:
        print("??error:csv_correlation:insufficent columns for cross mode", file=sys.stderr)
        sys.exit(1)

    if csv_file == "-":
        csv_file = sys.stdin

    csv_df = pd.read_csv(csv_file)

    csv_df[columns] = csv_df[columns].fillna(na_value)

    if r_skip > 1:
        in_s = range(0, len(csv_df), r_skip)
    else:
        in_s = range(len(csv_df))

    output_df = pd.DataFrame()
    if mode == "auto":
        for i in range(len(columns)):
            cn = columns[i]
            acf_res, confint, qstat, pvalues = tsa.stattools.acf(csv_df[cn].iloc[in_s], nlags=nlags, fft=True, alpha=0.05, qstat=True)
            output_df["ac_{}".format(cn)] = acf_res
            output_df["ac_ci_l_{}".format(cn)] = confint.T[0]
            output_df["ac_ci_u_{}".format(cn)] = confint.T[1]
    elif mode == "partial":
        for i in range(len(columns)):
            cn = columns[i]
            acf_res, confint = tsa.stattools.pacf(csv_df[cn].iloc[in_s], nlags=nlags, method="ols", alpha=0.05)
            output_df["ac_ci_l_{}".format(cn)] = confint.T[0]
            output_df["ac_ci_u_{}".format(cn)] = confint.T[1]
            output_df["ac_{}".format(cn)] = acf_res
    elif mode == "cross":
        for i in range(len(columns)):
            cn1 = columns[i]
            for j in range(i + 1, len(columns)):
                cn2 = columns[j]
                if nlags == 0:
                    output_df["cc_{}_{}".format(cn1, cn2)] = tsa.stattools.ccf(csv_df[cn1].iloc[in_s], csv_df[cn2].iloc[in_s])
                else:
                    output_df["cc_{}_{}".format(cn1, cn2)] = tsa.stattools.ccf(csv_df[cn1].iloc[in_s], csv_df[cn2].iloc[in_s])[:nlags]

    output_df.index.name = "index"
    output_df.to_csv(output_file)
