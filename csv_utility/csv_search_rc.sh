#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-08-15 13:24:48>
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
check_commands awk grep

usage_exit() {
    cat <<EOF 2>&1
to search keyword in csv file and to return the position:(row,col)
Usage: $SNAME [-w] [-l] keyword csv_file
arguments:
  keyword : keyword to search, grep regex pattern is available.
  csv_file: csv file

options:
  -l: one result as one line
  -w: keyword as word

remark:
  as assumption, there is only one header row in csv file.

EOF
    exit 1
}

while getopts lwh OPT
do
    case $OPT in
        l)  ONELINE=1
            ;;
        w)  WORD=1
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

KEY=$1
INPUT=$2

if [ "${INPUT}" = "-" ]; then
    TMPFILE="${TMPDIR}/${SNAME}_input.tmp"
    cat > ${TMPFILE}
    INPUT=${TMPFILE}
elif [ ! -e "${INPUT}" ]; then
    echo "??Error: file not found: ${INPUT}" 1>&2
    exit 1
fi

if [ "${WORD}" = "1" ]; then
    PATTERN="\b${KEY}\b"
else
    PATTERN="${KEY}"
fi
#----

GREP_RESULTS=($(grep -n -E "${PATTERN}" ${INPUT}))
echo "number of matched records: ${#GREP_RESULTS[@]}" 1>&2
RESULTS=()
for line in "${GREP_RESULTS[@]}"; do
    ROW=$(echo ${line}| awk -F: "{print \$1}")
    ROW=$((${ROW}-1))
    CS=$(echo ${line} | tr "," "\n")
    COLS=($(echo "${CS}"| grep -n -E "${PATTERN}" | awk -F: "{print \$1}"))
    for c in "${COLS[@]}"; do
	if [ "${ONELINE}" = "1" ]; then
	    RC="${ROW},${c}"
	else
	    RC="(${ROW},${c})"
	fi
	RESULTS=("${RESULTS[@]}" "${RC}")
    done
done
if [ "${ONELINE}" = "1" ]; then
    printf "%s\n" "${RESULTS[@]}"

else
    echo "${RESULTS[@]}"
fi

if [ "${TMPFILE}" != "" -a -e "${TMPFILE}" ]; then
    rm -f ${TMPFILE}
fi

#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

