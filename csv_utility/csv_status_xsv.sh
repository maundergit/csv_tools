#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-08-22 18:12:35>
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
check_commands xsv

usage_exit() {
    cat <<EOF 2>&1
print status of each column by 'xsv'
Usage: $SNAME [-c columns] [-f number] csv_file
options:
  -c columns: columns to analysis, 1-base, default=all
  -f number : less than this number of freqeuncy, default=(number of records)/10
EOF
    exit 1
}

while getopts c:f:h OPT
do
    case $OPT in
        c)  COLUMNS=$OPTARG
            ;;
        f)  FLIMIT=$OPTARG
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

PREFIX=${INPUT%.*}
SUFFIX=${INPUT#${INPUT%.*}.}
OUTPUT=${PREFIX}_status.csv

#----

NROWS=$(cat "${INPUT}"|wc -l )
NROWS=$((NROWS-1))

xsv stats --select "${COLUMNS}" "${INPUT}" --everything |tee "${OUTPUT}"
echo "-- ${OUTPUT} was created" 1>&2

FLIMIT=${FLIMIT:-$((NROWS/10))}
F_COLS=$(awk -F, "\$12 < ${FLIMIT} {print \$1\":\"\$12}" "${OUTPUT}")
echo "$(cat <<EOF

-- columns that have frequently values
${F_COLS}
EOF
    )"

if [ "${TMPFILE}" != "" -a -e "${TMPFILE}" ]; then
    rm -f ${TMPFILE}
fi

#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

