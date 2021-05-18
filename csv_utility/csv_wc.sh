#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-08-14 19:00:55>
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
check_commands nkf grep wc awk

usage_exit() {
    cat <<EOF 2>&1
command like 'wc' for csv
Usage: $SNAME (-c|-r|-t) csv_file
options:
  -c : number of columns
  -r : number of rows
  -t : line terminator
remark:
  as assumption, there is only one header row in csv file.
  number of rows means one without header row.
EOF
    exit 1
}

while getopts crth OPT
do
    case $OPT in
        c)  MODE=1
            ;;
        r)  MODE=2
            ;;
        t)  MODE=3
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
INPUT0=${INPUT}
if [ "${INPUT}" = "-" ]; then
    TMPFILE="${TMPDIR}/${SNAME}_input.tmp"
    cat > ${TMPFILE}
    INPUT=${TMPFILE}
    INPUT0="stdin"
elif [ ! -e "${INPUT}" ]; then
    echo "??Error: file not found: ${INPUT}" 1>&2
    exit 1
fi

#----
CHECK_CR=$(grep -l -zP "\r" ${INPUT})
CHECK_CRLF=$(grep -l -zP "\r\n" ${INPUT})
if [ "${CHECK_CRLF}" != "" ]; then
    CHECK_CR="CR+LF"
    TMPFILE2="${TMPDIR}/${SNAME}_input2.tmp"
    sed 's/\r//g' ${INPUT} > ${TMPFILE2}
    INPUT=${TMPFILE2}
elif [ "${CHECK_CR}" != "" ]; then
    CHECK_CR="CR"
    TMPFILE2="${TMPDIR}/${SNAME}_input2.tmp"
    sed 's/\r/\n/g' ${INPUT} > ${TMPFILE2}
    INPUT=${TMPFILE2}
else
    CHECK_CR="LF"
fi

OIFS=${IFS}
IFS=\|
HEADERS=($(awk 'NR==1 {print $0}' "${INPUT}" | tr "," "|"))
IFS=${OIFS}

MAX_HLEN=0
IC=0
IPOS=0
for h in "${HEADERS[@]}"; do
    if (( ${MAX_HLEN} < ${#h} )); then
	MAX_HLEN=${#h}
	IPOS=${IC}
    fi
    IC=$((${IC}+1))
done


NC=${#HEADERS[@]}
#NR=($(wc -l ${INPUT}))
#NR=$((${NR[0]}-1))
NR=$(csvstat --count ${INPUT} | awk '{print $3}')
CC=$(nkf -guess ${INPUT})
if [ "${MODE}" = "1" ]; then
    echo ${NC}
    exit 0
elif [ "${MODE}" = "2" ]; then
    echo ${NR}
    exit 0
elif [ "${MODE}" = "3" ]; then
    echo ${CHECK_CR}
    exit 0
fi

cat <<EOF
==== status of csv file: ${INPUT0}
charcter code      : ${CC}
line terminator    : ${CHECK_CR}
number of data rows: ${NR}
number of columns  : ${NC}

maximum length of column header : ${MAX_HLEN} at #${IPOS}
EOF

if [ "${TMPFILE}" != "" -a -e "${TMPFILE}" ]; then
    rm -f ${TMPFILE}
fi
if [ "${TMPFILE2}" != "" -a -e "${TMPFILE2}" ]; then
    rm -f ${TMPFILE2}
fi

#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

