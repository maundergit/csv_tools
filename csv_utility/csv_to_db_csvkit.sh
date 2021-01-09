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
to insret contents of csv file into db by csvkit
Usage: $SNAME [-i] [-d db_name] [-s number_of_rows] [-p primary_keys] table_name csv_file
arguments:

options:
  -i        : only printing sql to make db table
  -d db_name: name of data base
              url is available: ex. sqlite:///db_file, mysql://user:password@localhost:3306/database_name
              if db_name was one without protocol, sqlite3 is assumed.
              if this option was omitted, assuming sqlite3 db file, what name is table_name+".sqlite" , will be created.
  -p primary_keys: primary keys, with csv format
  -s number_of_rows: number of scaned rows for creatign table
EOF
    exit 1
}

while getopts id:p:s:h OPT
do
    case $OPT in
        i)  ONLY_CREATE=1
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

if [[ ${DBNAME} =~ :/ ]]; then
    URLS=(${DBNAME/:\/\/\// })
    DBTYPE=${URLS[0]}
    URL=${DBNAME}
else
    DBTYPE=sqlite
    DB_FILE_SQLITE3=${DBNAME}.sqlite3
    URL=sqlite:///${DB_FILE_SQLITE3}
fi

SCAN_ROWS=${SCAN_ROW:-20}
if [ "${PKEY}" != "" ];then
    PKEY_SQL=",PRIMARY KEY(${PKEY})"
fi

#----

SQL_CREATE=$(head -${SCAN_ROWS} ${INPUT} | csvsql -i ${DBTYPE} --no-constraints --tables ${TABLE_NAME}| sed -E "s/\);$/ ${PKEY_SQL});/")
if [ "${ONLY_CREATE}" = "1" ]; then
    echo "${SQL_CREATE}"
    exit
fi

# TBL_EXIST=$(${SQLITE_CMD} "${DB_FILE}" ".tables ${TABLE_NAME}")
TBL_EXIST=$(sql2csv --db ${URL} --query "select * from ${TABLE_NAME} limit 1;" 2>/dev/null)
if [ "${TBL_EXIST}" = "" ]; then
    echo "-- table:${TABLE_NAME} was not found, so that was created."
    # echo ${SQL}
    # ${SQLITE_CMD} "${DB_FILE_SQLITE3}" "${SQL_CREATE}"
    ${SQLITE_CMD} "${DB_FILE_SQLITE3}" "${SQL_CREATE}"
    echo "-- ${TABLE_NAME} in '${URL}' was created"
else
    # ROWS=$(${SQLITE_CMD} "${DB_FILE_SQLITE3}" "SELECT COUNT(*) FROM ${TABLE_NAME};")
    ROWS=$(sql2csv --db "${URL}" --query "SELECT COUNT(*) FROM ${TABLE_NAME};"| awk 'NR==2 {print $1}')
    echo "-- ${TABLE_NAME} in '${URL}' already has ${ROWS} records"
fi

csvsql --db ${URL} --no-create --tables ${TABLE_NAME} --insert ${INPUT}
if (( $? > 0 )); then
    echo "--error: "
else
    echo "-- ${TABLE_NAME} in '${URL}' was update"
fi

if [ "${TMPFILE}" != "" -a -e "${TMPFILE}" ]; then
    rm -f ${TMPFILE}
fi

#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

