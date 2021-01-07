#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-08-19 18:26:11>
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
check_commands sqlite3 csvsql sed head

usage_exit() {
    cat <<EOF 2>&1
inset contents of csv file into sqlitDB
Usage: $SNAME [-d db_name] [-s number_of_rows] [-p primary_keys] table_name csv_file
options:
  -d db_name:  name of data base
  -p primary_keys: primary keys, with csv format
  -s number_of_rows: number of scaned rows for creatign table
EOF
    exit 1
}

while getopts ad:p:s:h OPT
do
    case $OPT in
        a)  FLAG_A=1
            ;;
        d)  DBNAME=$OPTARG
            ;;
        p)  PKEY=$OPTARG
            ;;
        s)  SCAN_ROWS=$OPTARG
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

SQLITE_CMD=sqlite3

TABLE_NAME=$1
INPUT=$2
if [ "${INPUT}" = "-" ]; then
    TMPFILE="${TMPDIR}/${SNAME}_input.tmp"
    cat > ${TMPFILE}
    INPUT=${TMPFILE}
elif [ ! -e "${INPUT}" ]; then
    echo "??Error: file not found: ${INPUT}" 1>&2
    exit 1
fi

DBNAME=${DBNAME:-${TABLE_NAME}}
DB_FILE=${DBNAME}.sqlite3

SCAN_ROWS=${SCAN_ROW:-20}
if [ "${PKEY}" != "" ];then
    PKEY_SQL=",PRIMARY KEY(${PKEY})"
fi

#----

TBL_EXIST=$(${SQLITE_CMD} "${DB_FILE}" ".tables ${TABLE_NAME}")
if [ "${TBL_EXIST}" = "" ]; then
    echo "-- table:${TABLE_NAME} was not found, so that was created."
    SQL=$(head -${SCAN_ROWS} ${INPUT} | csvsql  --no-constraints --tables ${TABLE_NAME}| sed -E "s/\);$/ ${PKEY_SQL});/")
    # echo ${SQL}
    ${SQLITE_CMD} "${DB_FILE}" "${SQL}"
    echo "-- ${TABLE_NAME} in ${DB_FILE} was created"
else
    ROWS=$(${SQLITE_CMD} "${DB_FILE}" "SELECT COUNT(*) FROM ${TABLE_NAME};")
    echo "-- ${TABLE_NAME} in ${DBNAME} already has ${ROWS} records"
fi

csvsql --db sqlite:///${DB_FILE} --no-create --tables ${TABLE_NAME} --insert ${INPUT}
echo "-- ${TABLE_NAME} in ${DB_FILE} was update"

if [ "${TMPFILE}" != "" -a -e "${TMPFILE}" ]; then
    rm -f ${TMPFILE}
fi

#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

