#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-08-23 09:46:54>
#
#  Copyright (c) 2021 Masaharu N. Akei
#
#  This software is released under the MIT License.
#    http://opensource.org/licenses/mit-license.php
#----------------------------------------------------------------------
DTSTMP=$(date +%Y%m%dT%H%M%S)

DDIR=$(dirname $0)
SNAME=$(basename $0)
#DDIR_ABS=$(cd $(dirname ${DDIR}) && pwd)/$(basename $DDIR)
DDIR_ABS=$(realpath ${DDIR})
TMPDIR=/tmp


#----
cat <<EOF
csvtool transpose
csvtool call
csvtool replace  : replace columns with index key
csvtool pastecol : replace columns

xsv flatten   : print by transpose format
xsv frequency : frequently elements of each column
    xsv frequency --limit=3 input.csv |  awk -F, '$3>1 {print $0}'
xsv join      : inne, outer and cross join
xsv partition : split by column value and sore results into file
xsv search    :
xsv stats     :
xsv headers   :


Bit情報の時間変化を見る場合
1. decmpose bits status
   csv_uty.py --decompose_bit_string
2. timefrequency
   csv_trimtime.py --change_timefreq
3. taimefrequencyをキーとするグルーピングでのヒストグラム作成
   csv_status.py --group
4. Melting
   csv_uty.py --stack=
5. timeFrequencyをキーとする各ビットのPlot Scatter

EOF



#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

