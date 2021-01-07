#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-08-14 13:39:54>
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
TMPDIR=/tmp/${SNAME}.$$

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
check_commands awk sed seq csvlook fmt csv_multiindex_columns.py

usage_exit() {
    cat <<EOF 2>&1
to print names of columns in csv file
Usage: $SNAME [-t] [-c columns] [-n index_width] [-r nrows] csv_file

options:
  -t             : table format
  -c columns     : index of columns to print, ex: 1-10,51-60
  -n index_width : number of width of index, default=5
  -r nrows       : multiindex columns mode, nrows is number of rows of headers

remark:
  as assumption, there is only one header row in csv file.

EOF
    exit 1
}

while getopts ac:n:r:th OPT
do
    case $OPT in
        a)  FLAG_A=1
            ;;
        c)  COLUMNS=$OPTARG
            ;;
        n)  N_LENGTH=$OPTARG
            ;;
        r)  NROWS=$OPTARG
            ;;
        t)  TABLEF=1
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
N_LENGTH=${NLENGTH:-5}
NROWS=${NROWS:-1}

#----
INPUT=$(check_and_get_stdin "${INPUT}")


if (( ${NROWS} > 1 )); then
    CM_TMPFILE=$(make_tmpfile)
    ${DDIR}/csv_multiindex_columns.py --only_header --nrows=${NROWS} --to_single ${INPUT} > ${CM_TMPFILE}
    INPUT=${CM_TMPFILE}
fi

unset CNOS
OIFS=${IFS}
IFS=\|
HEADERS=($(awk 'NR==1 {print $0}' "${INPUT}" | sed "s/\r//g" | tr "," "|"))
IFS=${OIFS}

if [ "${COLUMNS}" != "" ]; then
    COLUMNS=$(echo ${COLUMNS}| tr "," " ")
    CNOS=()
    for v in ${COLUMNS}; do
	if [[ ${v} =~ - ]]; then
	    v2=(${v/-/ })
	    CNOS=("${CNOS[@]}" $(seq ${v/-/ }))
	elif [[ ${v} =~ [0-9]+ ]]; then
	    CNOS=("$CNOS[@]}" ${v})
	fi
    done
else
    NH=$((${#HEADERS[@]}-1))
    CNOS=$(seq 0 ${NH})
fi

RES=$(
    for C in ${CNOS[@]}; do
	v=${HEADERS[${C}]}
	if [ "${v}" != "" ]; then 
	    printf "%0${N_LENGTH}d:%s |" ${C} "${v}"
	fi
    done 
   )
RES=${RES::-1}

if [ "${TABLEF}" = "1" ]; then
    echo -e "${RES}" | fmt | sed -E "s/\|([0-9]{${N_LENGTH}})/,\1/g" | csvlook -H
else
    OIFS=${IFS}
    IFS=\|
    echo -e "${RES}" | tr "|" "\n"
    IFS=${OIFS}
fi

remove_tmpdir

#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

