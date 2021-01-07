#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-09-06 14:12:45>
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
# TMPDIR=/tmp/${SNAME}.$$

check_commands() {
    # check_commands ls dataflow find
    # usage: check_commands "${array[@]}"
    CHK_CMDS=("$@")
    unset MES
    for c in "${CHK_CMDS[@]}"; do
        if [ "$(which ${c})" = "" ]; then
            MES="${MES}-- error: not found $c\n"
        fi
    done
    if [ "${MES}" != "" ]; then
        echo -e "${MES}" 1>&2
        exit 1
    fi
}


usage_exit() {
    cat <<EOF 2>&1
convert matrix data into (x,y,v).
Usage: $SNAME [-n] csv_file
options:
  -n : no header mode

remark:
  output file may be used by csv_plot_heatmap.py, and so on.

example1:
  csv_matrix.sh test_matrix.csv |csv_plot_heatmap.py --format=html --side_hist - ROW_ID COL_ID value >test.html

example2:
  csv_matrix.sh test_matrix.csv
input=
,A,B,C,D,E
Z,1,2,3,4,5
Y,6,7,8,9,10

output:
ROW_ID,COL_ID,value
Z,A,1
Z,B,2
Z,C,3
Z,D,4
Z,E,5
Y,A,6
Y,B,7
Y,C,8
Y,D,9

EOF
    exit 1
}

while getopts nd:h OPT
do
    case $OPT in
        n)  NOHEADER=1
            ;;
        d)  VALUE_D=$OPTARG
            ;;
        h)  usage_exit
            ;;
        \?) usage_exit
            ;;
    esac
done
shift $((OPTIND - 1))

if [ "$1" = "" ];  then
    usage_exit
fi

INPUT=$1
# INPUT=$(check_and_get_stdin "${INPUT}")

PREFIX=${INPUT%.*}
SUFFIX=${INPUT#${INPUT%.*}.}
OUTPUT=${PREFIX}.raw

#----
OIFS=${IFS}
IFS=\|
HEADERS=($(awk 'NR==1 {print $0}' "${INPUT}" | sed "s/\r//g" | tr "," "|"))
IFS=${OIFS}

NCOLS=${#HEADERS[@]}

if [ "${NOHEADER}" = "" ]; then
    NR0=1
else
    NR0=0
fi
NR=-1
echo "ROW_ID,COL_ID,value"
while read LINE;do
    NR=$((NR+1))
    OIFS=${IFS}; IFS=\|;
    COLS=($(echo "${LINE}" | sed "s/\r//g" | tr "," "|"))
    IFS=${OIFS}
    if (( NR < NR0 )); then
       continue
    fi
    if [ "${NOHEADER}" = "" ]; then
	HR=${COLS[0]}
	NC0=1
	for ((i=NC0;i <NCOLS; i++)); do
	    echo "${HR},${HEADERS[${i}]},${COLS[${i}]}"
	done
    else
	HR=${NR}
	NC0=0
	for ((i=NC0;i <NCOLS; i++)); do
	    echo "${HR},${i},${COLS[${i}]}"
	done
    fi
done < ${INPUT}


#----
# remove_tmpdir
#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

