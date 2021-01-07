#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-08-14 09:11:16>
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
function db_mysql(){
    # 【MySQL】CSVファイルをデータベースにインポートする | (株)シャルーン http://blog.chatlune.jp/2018/03/01/mysql-import-csv/
    MYSQL_COMMAND="mysql"
    DUMP=$1
    DBNAME=$2
    TABLE=$3
    INDEX_NAME=$4
    INPUT=$5
    PRE_SQL=$6

    OIFS=${IFS}
    IFS=\|
    COLUMNS=($(head -1 "${INPUT}" | tr "," "|"))
    IFS=${OIFS}

    if [ "${DB_USER}" != "" ]; then
	DB_OPT="${DB_OPT} -u ${DB_USER} -p"
    fi
    
    SQL=("CREATE DATABASE IF NOT EXISTS ${DBNAME} DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;")
    SQL=("${SQL[@]}" "use ${DBNAME};")
    unset FIELDS
    for c in ${COLUMNS[@]}; do
	c=$(echo ${c}| tr -d '"')
	FIELDS="${FIELDS}\"${c}\" VARCHAR(256),"
    done
    FIELDS="${FIELDS} PRIMARY KEY (\`${INDEX_NAME}\`)"
    SQL=("${SQL[@]}" "CREATE TABLE IF NOT EXISTS ${TABLE}(${FIELDS});")

    SQL=("${SQL[@]}" "SHOW CREATE TABLE ${TABLE}\G" )
    TMPFILE="csv_to_db_$$.csv"
    awk 'NR>1 {print $0}' "${INPUT}" > ${TMPFILE}
    SQL=("${SQL[@]}" "LOAD DATA LOCAL INFILE \"${TMPFILE}\" INTO TABLE ${TABLE} FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"';")
    SQL=("${SQL[@]}" "SHOW TABLE STATUS WHERE NAME=\"${TABLE}\"\G")
    SQL=("${SQL[@]}" "SELECT * FROM ${TABLE} LIMIT 3;")
    
    ESQL="${PRE_SQL}${SQL[@]}"
    if [ "${DUMP}" = "0" ]; then
	${MYSQL_COMMAND} ${DB_OPT} --execute="${ESQL}"
    else
	echo "#-- SQL statements"
	echo "-- DROP DATABSE IF EXISTS ${DBNAME};-- use ${DBNAME};-- DROP TABLE IF EXISTS ${TABLE}; ${ESQL}" | sed -E "s/; */;\n/g; s/\G */\G\n/g"
    fi
    rm ${TMPFILE}
}
function db_sqlite(){
    # CSV形式のデータをファイルからインポート(.importコマンド) | SQLite入門 https://www.dbonline.jp/sqlite/sqlite_command/index7.html
    SQLITE_COMMAND="sqlite3"
    DUMP=$1
    DBNAME=$2
    TABLE=$3
    INDEX_NAME=$4
    INPUT=$5
    PRE_SQL=$6
    
    OIFS=${IFS}
    IFS=\|
    COLUMNS=($(head -1 "${INPUT}" | tr "," "|"))
    IFS=${OIFS}
    
    SQL=()
    DOTSQL=()
    
    unset FIELDS
    for c in ${COLUMNS[@]}; do
	c=$(echo ${c}| tr -d '"')
	if [ "${c}" = "${INDEX_NAME}" ]; then
	    dtype="TEXT PRIMARY KEY"
	else
	    dtype="TEXT"
	fi
	FIELDS="${FIELDS}\"${c}\" ${dtype},"
    done
    FIELDS="${FIELDS::-1}"
    SQL=("${SQL[@]}" "CREATE TABLE IF NOT EXISTS ${TABLE}(${FIELDS});")

    DOTSQL=("${DOTSQL[@]}" ".tables ${TABLE};" )
    DOTSQL=("${DOTSQL[@]}" ".mode csv;")
    DOTSQL=("${DOTSQL[@]}" ".import ${INPUT} ${TABLE};")
    DOTSQL=("${DOTSQL[@]}" ".schaema ${TABLE};")
    
    ESQL="${PRE_SQL}${SQL[@]}"
    EDOTSQL="${DOTSQL[@]}"
    if [ "${DUMP}" = "0" ]; then
	# echo ${SQLITE_COMMAND} ${DB_OPT} ${DBNAME} "${ESQL}"
	${SQLITE_COMMAND} ${DB_OPT} ${DBNAME} "${ESQL}"
	sqlite3 -separator "," "${DBNAME}" ".import \"${INPUT}\" ${TABLE}"
	sqlite3 -separator "," "${DBNAME}" ".schema ${TABLE}"
	sqlite3 -separator "," "${DBNAME}" "SELECT * FROM ${TABLE} LIMIT 3;"
    else
	echo "#-- SQL statements"
	echo "-- DROP TABLE IF EXISTS ${TABLE};${ESQL}${EDOTSQL}SELECT * FROM ${TABLE} LIMIT 3;" | sed -E "s/; */;\n/g; s/\G */\G\n/g"
    fi
}
check_commands awk sed csvcut mysql sqlite3

usage_exit() {
    cat <<EOF 2>&1
to insert csv data into database
Usage: $SNAME [-d db_type] [-u db_user] [-p] [-c columns] db_name table_name index_name csv_file [sql]

arguments:
   db_name    : name of database. if db_type was "sqlite3", then that means name of file.
   table_name : name of table
   index_name : name of column that means index/primary key.
   csv_file   : name of csv file, that has names of columns at first row.
   sql        : sql statments that will be executed at first.

options:
   -d db_type : name of database, [mysql,sqlite3]: default=sqlite3
   -u db_user : user name for database
   -c columns : selected columns. ex. 1-5,20-30
   -p         : dump sql string, without execution

example: 
  ${SNAME} -d mysql -u root sampleDB testTBL ID sample.csv "use sampleDB;DROP TABLE IF EXISTS testTBL;"
  ${SNAME} -d sqlite3 sampleDB.sqlite3 testTBL ID sample.csv "DROP TABLE IF EXISTS testTBL;"

remark:
  charcode in csv_file must be utf-8.
  in db, type of data for each columns is VARCHAR(256) for mysql or TEXT for sqlite3. 
  if you want to change the type, use '-p' and edit sql statements that is executed by hand. 
  or you may use 'head -20 csv_file | csvsql -i db_type' to make sql statements for creating table.
  As assumption, there is only one header row in csv file.

  Alse you can use 'csvsql --overwrite --tables table_name --db db_type:///csv_file --insert csv_file'
  
EOF
    exit 1
}

while getopts c:d:pu:h OPT
do
    case $OPT in
        c)  SELECTED_COLUMNS=$OPTARG
            ;;
        d)  DB_TYPE=$OPTARG
            ;;
        p)  DUMP=1
            ;;
        u)  DB_USER=$OPTARG
            ;;
        h)  usage_exit
            ;;
        \?) usage_exit
            ;;
    esac
done
shift $((OPTIND - 1))

if [ "$4" = "" ];  then
    usage_exit
fi

DBNAME=$1
TABLE=$2
INDEX_NAME=$3
INPUT=$4
PRE_SQL=$5

DUMP=${DUMP:-0}
DB_TYPE=${DB_TYPE:-sqlite3}

if [ "${INPUT}" = "-" ]; then
    TMPFILE_0="${TMPDIR}/${SNAME}_input.tmp"
    cat > ${TMPFILE_0}
    INPUT=${TMPFILE_0}
elif [ ! -e "${INPUT}" ]; then
    echo "??Error: file not found: ${INPUT}" 1>&2
    exit 1
fi

#----

if [ "${SELECTED_COLUMNS}" != "" ]; then
    if [ "$(which csvcut)" = "" ]; then
	echo "#-- error: csvcut ws not found, '-c' option was not available." 1>&2
	exit 1
    fi
    TMPFILE="csv_to_db_cut_$$.csv"
    echo "#-- cut columns: ${SELECTED_COLUMNS}" 1>&2
    csvcut --columns "${SELECTED_COLUMNS}" ${INPUT} > ${TMPFILE}
    INPUT_ORG=${INPUT}
    INPUT=${TMPFILE}
fi

if [ "${DB_TYPE}" = "mysql" ]; then
    RES=$(db_mysql ${DUMP} ${DBNAME} ${TABLE} "${INDEX_NAME}" "${INPUT}" "${PRE_SQL}")
elif [ "${DB_TYPE}" = "sqlite3" ]; then
    RES=$(db_sqlite ${DUMP} ${DBNAME} ${TABLE} "${INDEX_NAME}" "${INPUT}" "${PRE_SQL}")
else
    echo "-- error: unknown database type: ${DB_TYPE}" 1>&2
fi
if [ "${SELECTED_COLUMNS}" != "" ]; then
    echo "${RES}" | sed -E "s/${INPUT}/${INPUT_ORG}/g"
else
    echo "${RES}"
fi
if [ -e "${TMPFILE}" ]; then
    rm -f ${TMPFILE}
fi

if [ "${TMPFILE_0}" != "" -a -e "${TMPFILE_0}" ]; then
    rm -f ${TMPFILE_0}
fi

#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

