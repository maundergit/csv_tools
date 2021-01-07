#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-08-14 15:16:27>
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
check_commands csvcut grep awk seq

usage_exit() {
    cat <<EOF 2>&1
to split ONE csv file into some csv files, that may have too many columns.
Usage: $SNAME [-n limit_columsn] index_column csv_file
arguments:
  index_column : column label that index column has.
                 in all results, there is this column.
                 if number, then as 0-base index number of fields.
options:
  -n limit_columns : maximum number of columns that one csv file has.
                     this limit may be given by limitation of database.
                     default is 2000
remark:
  as assumption, there is only one header row in csv file.

example:
${SNAME} 0 sample.csv
${SNAME} ID sample.csv

EOF
    exit 1
}

while getopts an:h OPT
do
    case $OPT in
        a)  FLAG_A=1
            ;;
        n)  LIMITC=$OPTARG
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

INDEX_COLUMN=$1
INPUT=$2

if [ "${INPUT}" = "-" ]; then
    TMPFILE="${TMPDIR}/${SNAME}_input.tmp"
    cat > ${TMPFILE}
    INPUT=${TMPFILE}
elif [ ! -e "${INPUT}" ]; then
    echo "??Error: file not found: ${INPUT}" 1>&2
    exit 1
fi

LIMITC=${LIMITC:-2000}

BINPUT=$(basename ${INPUT})
PREFIX=${BINPUT%.*}
SUFFIX=${BINPUT#${BINPUT%.*}.}

#----
OIFS=${IFS}
IFS=\|
HEADERS=($(awk 'NR==1 {print $0}' "${INPUT}" | sed "s/\r//g" | tr "," "|"))
IFS=${OIFS}
NH=$((${#HEADERS[@]}-1))

unset INO
if [[ ${INDEX_COLUMN} =~ ^[0-9]+$ ]]; then
    INO=${INDEX_COLUMN}
    INDEX_COLUMN=${HEADERS[$INO]}
else
    # if INDEX_COLUMN was not index of column, it will be searched in headers.
    for idx in $(seq 0 ${NH}); do
	if [ "${INDEX_COLUMN}" = "${HEADERS[${idx}]}" ]; then
	    INO=${idx}
	    break
	fi
    done
    if [ "${INO}" = "" ]; then
	echo "#-- error: index column was not found: ${INDEX_COLUMNS}" 1>&2
	exit 1
    fi
fi

echo "#-- csv file: ${INPUT}"
echo "    number columns: ${NH}"
echo "    index column  : ${INDEX_COLUMN}(${INO})"

# get number of splitted files.
N=$(((${NH}+1)/(${LIMITC}-1)+1))
for ((idx=0;idx<N;idx++)); do
    # get index of column of start in each file
    S0=$(((${LIMITC}-1)*${idx}))
    if (( ${S0} > ${NH} )); then
	break
    fi
    S1=$((${S0}+${LIMITC}-1-1))
    S1=$((${S1} > ${NH} ? ${NH}: ${S1}))

    # csvcut use 1-base index as index of columns
    SS0=$((${S0}+1))
    SS1=$((${S1}+1))
    SINO=$((${INO}+1))
    CS=$(echo $(seq ${SS0} ${SS1})|tr " " ",")
    
    # add index column if it was not included.
    CHK=$(echo ${CS}| grep -l -P "\b${SINO}\b" 2>&1)
    if [ "${CHK}" = "" ]; then
	CS="${SINO},${CS}"
    fi
    FNAME=${PREFIX}_$(printf "%03d" ${idx}).csv
    echo "-- columns: ${S0} to ${S1} into ${FNAME}"
    csvcut --columns ${CS} ${INPUT} > ${FNAME}
done

if [ "${TMPFILE}" != "" -a -e "${TMPFILE}" ]; then
    rm -f ${TMPFILE}
fi

#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

