#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-08-29 15:49:03>
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
TMPDIR=/tmp/${SNAME}.$$

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
check_and_get_stdin(){
    if [ "${INPUT}" = "-" ]; then
	if [ ! -e "${TMPDIR}" ]; then
	    mkdir "${TMPDIR}"
	fi
	TMPFILE_INPUT="${TMPDIR}/${SNAME}_input.tmp"
	cat > ${TMPFILE_INPUT}
	INPUT=${TMPFILE_INPUT}
    elif [ ! -e "${INPUT}" ]; then
	echo "??Error: file not found: ${INPUT}" 1>&2
	exit 1
    fi
    echo ${INPUT}
}
remove_tmpdir(){
    if [[ "${TMPDIR}" != "" && "${TMPDIR}" =~ ${SNAME} && -e "${TMPDIR}" ]]; then
	rm -rf "${TMPDIR}"
    fi
}
make_tmpfile(){
    ID=$1
    if [[ "${TMPDIR}" != "" && ! -e "${TMPDIR}" ]]; then
	mkdir "${TMPDIR}"
    fi
    FN="${TMPDIR}/${ID}_$$.tmp"
    echo "${FN}"
}
check_commands csvtotable csvcut head tail

usage_exit() {
    cat <<EOF 2>&1
convert csv file into html format
Usage: $SNAME [-c columns] [-r row0,row1] csv_file
arguments:
  csv_file : path of csv file
options:
  -c columns: list of columns, ex. 1,5-10
  -r row0,row1 : range of rows to print
EOF
    exit 1
}

while getopts ac:r:h OPT
do
    case $OPT in
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
INPUT=$(check_and_get_stdin "${INPUT}")

PREFIX=${INPUT%.*}
SUFFIX=${INPUT#${INPUT%.*}.}
OUTPUT=${PREFIX}.html

#----

if [ "${ROWS}" != "" ]; then
    TMPOUT=$(make_tmpfile rows)
    if [[ "${ROWS}" =~ ^([0-9]+),([0-9]+)$ ]]; then
	R0=${BASH_REMATCH[1]}
	R1=${BASH_REMATCH[2]}
	if (( R1 < R0 )); then
	    echo "-- invalid range of rows: ${ROWS}" 1>&2
	    exit 1
	fi
	(head -1 ${INPUT};head -$((R1+1)) ${INPUT}| tail -$((R1-R0+1))) > ${TMPOUT}
	INPUT=${TMPOUT}
    else
	exit 1
    fi
fi

if [ "${COLUMNS}" = "" ]; then
    csvtotable -o ${INPUT} ${OUTPUT}
else
    TMPOUT=$(make_tmpfile csv)
    csvcut --columns ${COLUMNS} "${INPUT}" > ${TMPOUT}
    csvtotable -o ${TMPOUT} ${OUTPUT}
fi

echo "-- ${OUTPUT} was created"

#----
remove_tmpdir
#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

