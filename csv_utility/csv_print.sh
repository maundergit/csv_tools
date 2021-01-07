#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-08-15 13:52:05>
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
function stderr_out(){
    MESSAGES=("$@")
    for m in "${MESSAGES[@]}"; do
	echo "${m}" 1>&2
    done
}
check_commands awk wc

usage_exit() {
    cat <<EOF 2>&1
to print contents around given (row,col) in csv file.
Usage: $SNAME [-n] [-c int]  [-r int] csv_file row col
arguments:
  row : index of row, integer
  col : index of column, integer
options:
  -c int: half width of view for columns
  -r int: half width of view for rows
  -n    : row number mode

remark:
  as assumption, there is only one header row in csv file.

EOF
    exit 1
}

while getopts c:nr:h OPT
do
    case $OPT in
        c)  HWC=$OPTARG
            ;;
	n) NRMODE=1
	   ;;
        r)  HWR=$OPTARG
            ;;
        h)  usage_exit
            ;;
        \?) usage_exit
            ;;
    esac
done
shift $((OPTIND - 1))

if [ "$3" = "" ];  then
    usage_exit
fi

INPUT=$1
ROW=$2
COL=$3

if [ "${INPUT}" = "-" ]; then
    TMPFILE="${TMPDIR}/${SNAME}_input.tmp"
    cat > ${TMPFILE}
    INPUT=${TMPFILE}
elif [ ! -e "${INPUT}" ]; then
    echo "??Error: file not found: ${INPUT}" 1>&2
    exit 1
fi

HWR=${HWR:-3}
HWC=${HWC:-3}

PREFIX=${INPUT%.*}
SUFFIX=${INPUT#${INPUT%.*}.}

#----
OIFS=${IFS}
IFS=\|
HEADERS=($(awk 'NR==1 {print $0}' "${INPUT}" | sed "s/\r//g" | tr "," "|"))
IFS=${OIFS}
NR=($(wc -l ${INPUT}))
NR=${NR[0]}
NR=$((NR-1))
NC=${#HEADERS[@]}
R0=$((ROW-HWR < 1 ? 1: ROW-HWR))
R1=$((ROW+HWR > NR ? NR: ROW+HWR))
C0=$((COL-HWC < 1 ? 1: COL-HWC))
C1=$((COL+HWC > NC ? NC: COL+HWC))

C0=$((C0-1))
C1=$((C1-1))

WC=$((C1-C0+1))

# print header
R=$(IFS=,; echo "${HEADERS[*]:${C0}:${WC}}")
if [ "${NRMODE}" = "1" ]; then
    echo "RNO,${R}"
else
    echo "${R}"
fi

# print rows
IR=0
while read LINE; do
    COLS=($(echo ${LINE} | tr "," " "| sed "s/\r//g"))
    if (( IR >= R0 && IR <= R1 )); then
	R=$(IFS=,;echo "${COLS[*]:${C0}:${WC}}")
	if [ "${NRMODE}" = "1" ]; then
	    echo "${IR},${R}"
	else
	    echo "${R}"
	fi
    elif (( IR > R1 )); then
	break
    fi
    IR=$((IR+1))
done < ${INPUT}

if [ "${TMPFILE}" != "" -a -e "${TMPFILE}" ]; then
    rm -f ${TMPFILE}
fi

#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

