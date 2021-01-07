#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-08-29 10:46:43>
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
# TMPDIR=/tmp/${SNAME}.$$

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

check_commands csvtool grep head tr date

usage_exit() {
    cat <<EOF 2>&1
to estimate data type of each column
Usage: $SNAME [-i] [-c columns] [-r number] [-v] csv_file
arguments:
  csv_file : path of csv file
options:
  -i        : print index of column, 1-base
  -c columns: indexes of columns to parse, 1-base ex.1,3-10
  -r number : number of rows to scan, default=10
  -v        : verbose

example:
  ${SNAME} -c 1-100 big_sample_arb.csv | awk '$2=="binary" {print $0}'
  ${SNAME} -i -c 1-20 -v big_sample_arb.csv

remark:
  
EOF
    exit 1
}

while getopts ic:r:vh OPT
do
    case $OPT in
	i)  INDEX_MODE=1
	    ;;
        c)  COLUMNS=$OPTARG
            ;;
        r)  MROWS=$OPTARG
            ;;
	v)  VERBOSE=1
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

MROWS=${MROWS:-10}
COLUMNS=${COLUMNS:-all}

PREFIX=${INPUT%.*}
SUFFIX=${INPUT#${INPUT%.*}.}
OUTPUT=${PREFIX}.raw

function get_list_of_columns(){
    COLUMNS=$1
    if [ "${COLUMNS}" = "all" -o -z "{$COLUMNS}" ]; then
	echo ""
	return
    fi
    IFS=, CS=(${COLUMNS})
    IFS=${OIFS}
    for v in ${CS[@]}; do
	if [[ "${v}" =~ ^([0-9]+)-([0-9]+)$ ]]; then
	    v1=${BASH_REMATCH[1]}
	    v2=${BASH_REMATCH[2]}
	    SS=($(seq -s" " ${v1} ${v2}))
	    COLS=("${COLS[@]}" ${SS[@]})
	else
	    COLS=("${COLS[@]}" ${v} )
	fi
    done
    echo ${COLS[@]}
}
function get_dtype(){
    D=("$@")
    CS=$(echo ${D[@]} | tr -d " " | sed -e 's/\b\(0b\|0x\)//g')
    if [[ "${CS}" =~ ^[01]+$ ]]; then
	DTYPE="binary"
#    elif [[ "${CS}" =~ ^[0-7]+$ ]]; then
#	DTYPE="oct"
    elif [[ "${CS}" =~ ^[[:digit:]]+$ ]]; then
	DTYPE="int"
    elif [[ "${CS}" =~ ^[0-9a-fA-F]+$ ]]; then
	DTYPE="hex"
    elif [[ "${CS}" =~ ^([[:digit:]]|\.)+$ ]]; then
	DTYPE="float"
    else
	if [[ "${CS}" =~ ^[0-9:/-]+$ ]]; then
	    CHK=0
	    for v in ${D[@]}; do
		if [ "$(LANG=C date --date="${v}" 2>/dev/null )" = "" ]; then
		    CHK=1
		fi
	    done
	else
	    CHK=1
	fi
	if [ "${CHK}" = "1" ]; then
	    DTYPE="string"
	else
	    DTYPE="date"
	fi
    fi
    echo ${DTYPE}
}    

#----

COLS=($(get_list_of_columns ${COLUMNS} ))

NL=0
head -$((MROWS+1)) "${INPUT}" | csvtool transpose - | tr "," " "| tr -d "'\"" | while read LINE; do
    NL=$((NL+1))
    if (( ${#COLS[@]} > 0 )); then
	CHK=$(echo "${COLS[@]}" | grep -E "\b${NL}\b")
	if [ "${CHK}" = "" ]; then
	    continue
	fi
    fi
    RS=(${LINE})
    COL_NAME=${RS[0]}
    CS=$(echo ${RS[@]:1} | tr -d " ")

    DTYPE=$(get_dtype ${RS[@]:1})

    if [ "${INDEX_MODE}" = "1" ]; then
	LNO=$(printf "%04d:" ${NL})
    fi
    if [ "${VERBOSE}" = "1" ]; then
	echo "${LNO}${COL_NAME} ${DTYPE}	${RS[@]:1:6}"
    else
	echo "${LNO}${COL_NAME} ${DTYPE}"
    fi
    if (( ${#COLS[@]} > 0 )); then
	if (( "${NL}" == "${COLS[-1]}" )); then
	    break
	fi
    fi
done

#----
remove_tmpdir
#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

