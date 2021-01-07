#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-09-17 15:48:07>
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


#---- 
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

check_commands xsv tr

usage_exit() {
    cat <<EOF 2>&1
join two csv file into one csv file
Usage: $SNAME [-m mode] columns_1 csv_file_1 columns_2 csv_file_2
Usage: $SNAME -s [-m mode] columns csv_file_1 csv_file_2
options:
  -s     : use same names of columns to join
  -m mode: join mode, l=left, r=right, f=full, default=l

example:
  csv_join.sh A,B test1.csv A,B test2.csv
  csv_join.sh -s A,B test1.csv test2.csv

EOF
    exit 1
}

while getopts sm:h OPT
do
    case $OPT in
        s)  SAME=1
            ;;
        m)  MODE=$OPTARG
            ;;
        h)  usage_exit
            ;;
        \?) usage_exit
            ;;
    esac
done
shift $((OPTIND - 1))

if [ "${SAME}" = "" -a "$4" = "" ];  then
    usage_exit
elif [ "${SAME}" = "1" -a "$3" = "" ];  then
    usage_exit
fi

if [ "${SAME}" = "" ];then
    COLS_1=$1
    INPUT_1=$2
    COLS_2=$3
    INPUT_2=$4
else
    COLS_1=$1
    INPUT_1=$2
    COLS_2=$1
    INPUT_2=$3
fi

INPUT_1_BASE=$(basename ${INPUT_1})
INPUT_2_BASE=$(basename ${INPUT_2})

PREFIX_1=${INPUT_1_BASE%.*}
PREFIX_2=${INPUT_2_BASE%.*}
OUTPUT=${OUTPUT:-${INPUT_1_BASE}_${INPUT_2_BASE}_join.csv}

INPUT=${INPUT_1}
INPUT_1=$(check_and_get_stdin)
INPUT=${INPUT_2}
INPUT_2=$(check_and_get_stdin)


MODE=${MODE:-l}

# INPUT=$(check_and_get_stdin "${INPUT}")
if [ "${MODE}" = "l" ]; then
    XOPT="--left"
    COPT="--left"
elif [ "${MODE}" = "r" ]; then
    XOPT="--right"
    COPT="--right"
elif [ "${MODE}" = "f" ]; then
    XOPT="--full"
    COPT="--outer"
fi

#----

if [ "${COLS_1}" = "${COLS_2}" ]; then
    COLUMNS=($(xsv headers -j "${INPUT_1}"))
    HEADERS=($(xsv headers -j "${INPUT_2}"))
    CS=($(echo "${COLS_2}"|tr "," " "))
    for c in "${HEADERS[@]}"; do
	CHK=0
	for c2 in "${CS[@]}"; do
	    if [ "${c}" = "${c2}" ]; then
		CHK=1
		break
	    fi
	done
	if [ "${CHK}" = "0" ]; then
	    COLUMNS=("${COLUMNS[@]}" "${c}")
	fi
    done
    COLUMNS=$(echo "${COLUMNS[@]}" | tr " " ",")
    xsv join ${XOPT} ${COLS_1} ${INPUT_1} ${COLS_2} ${INPUT_2} |xsv select ${COLUMNS} -
else
    xsv join ${XOPT} ${COLS_1} ${INPUT_1} ${COLS_2} ${INPUT_2}
fi



#----
remove_tmpdir
#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

