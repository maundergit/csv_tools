#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-08-14 18:42:49>
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

usage_exit() {
    cat <<EOF 2>&1
make simple dummy record with csv format
Usage: $SNAME [-q] number_of_data_rows number_of_columns
options:
  -q : quoting cell value.

EOF
    exit 1
}

while getopts qh OPT
do
    case $OPT in
        q)  QUOTE=1
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

NROWS=$1
NCOLUMNS=$2
QUOTE=${QUOTE:-0}

#----
ROWL=()
for ((COLS=0;COLS<${NCOLUMNS};COLS++)); do
    C=$(printf "COL_%04d" ${COLS})
    ROWL=("${ROWL[@]}" ${C})
done
echo "${ROWL[@]}" | tr " " ","
for ((ROWS=0;ROWS<${NROWS};ROWS++)); do
    ROWL=()
    echo -en "-- processing rows : ${ROWS}\r" 1>&2
    for ((COLS=0;COLS<${NCOLUMNS};COLS++)); do
	RS=$(printf "%04x" ${ROWS})
	CS=$(printf "%04x" ${COLS})
	C="${RS}${CS}"
	if [ "${QUOTE}" = "1" ]; then
	    C="\"${C}\""
	fi
	ROWL=("${ROWL[@]}" "${C}")
    done
    echo "${ROWL[@]}" | tr " " ","
done




#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

