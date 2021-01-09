#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-08-15 12:03:13>
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

check_commands csvcut head tail


usage_exit() {
    cat <<EOF 2>&1
command like head for csv.
Usage: $SNAME [-t] [-c range_of_columns] [-r number_of_rows] csv_file 
options:
  -c range_of_columns: range of columns as 1-base index ex.:16,20-31
  -r numbr_or_rows   : number of rows to view
  -t                 : tail mode
remark:
  as assumption, there is only one header row in csv file.

EOF
    exit 1
}

while getopts tc:r:h OPT
do
    case $OPT in
        t)  MODE="tail"
            ;;
        c)  COLUMNS=$OPTARG
            ;;
        r)  ROWS=$OPTARG
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
if [ "${INPUT}" = "-" ]; then
    TMPFILE="${TMPDIR}/${SNAME}_input.tmp"
    cat > ${TMPFILE}
    INPUT=${TMPFILE}
elif [ ! -e "${INPUT}" ]; then
    echo "??Error: file not found: ${INPUT}" 1>&2
    exit 1
fi

ROWS=${ROWS:-5}
MODE=${MODE:-head}
#----
OIFS=${IFS}
IFS=\|
HEADERS=($(awk 'NR==1 {print $0}' "${INPUT}" | sed "s/\r//g" | tr "," "|"))
IFS=${OIFS}
NC=${#HEADERS[@]}
if (( NC < 10 )); then
    COLUMNS=${COLUMNS:-1-${NC}}
else
    COLUMNS=${COLUMNS:-1-10}
fi

NR=$(cat ${INPUT}| wc -l)
NR=$((NR-1))
if (( NR < ROWS )); then
    ROWS=${NR}
fi

stderr_out "$(cat <<EOF
#-- mode           : ${MODE}
#-- columns(1-base): ${COLUMNS}
#-- nrows of data  : ${ROWS}
EOF
	     )"
ROWS=$((${ROWS}+1))
if [ "${MODE}" = "tail" ]; then
    head -1 ${INPUT} | csvcut -c ${COLUMNS}
    tail --lines=${ROWS} ${INPUT} | csvcut -c ${COLUMNS}
else
    head -${ROWS} ${INPUT} | csvcut -c "${COLUMNS}"
fi

if [ "${TMPFILE}" != "" -a -e "${TMPFILE}" ]; then
    rm -f ${TMPFILE}
fi

#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

