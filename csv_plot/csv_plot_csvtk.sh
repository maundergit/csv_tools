#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-08-29 17:17:20>
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
# TMPDIR=/tmp
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

check_commands csvtk

usage_exit() {
    cat <<EOF 2>&1
plot histogram by graphical character.
Usage: $SNAME [-s] csv_file x_column y_column [group_column]
Usage: $SNAME -t csv_file column
arguments:
  csv_file    : path of csv file
  x_column    : name of column for x
  y_column    : name of column for y
  column      : name of column to make histogram
  group_column: name of column for grouping

options:
  -s : scatter plot
  -t : histogram mode for one colun


example:
  ${SNAME} -s big_sample_arb.csv COL_0008 COL_0033 COL_0006
  ${SNAME} -t test_plot.csv COL_0000

EOF
    exit 1
}

while getopts std:h OPT
do
    case $OPT in
        s)  SCATTER=1
            ;;
        t)  HIST=1
            ;;
        d)  VALUE_D=$OPTARG
            ;;
        h)  usage_exit
            ;;
        \?) usage_exit
            ;;
    esac
done
shift $((OPTIND - 1))

if [ "${HIST}" = "" -a "$3" = "" ];  then
    usage_exit
elif [ "${HIST}" = "1" -a "$2" = "" ];  then
    usage_exit
fi

INPUT=$1
INPUT=$(check_and_get_stdin "${INPUT}")

XCOL=$2
YCOL=$3
GROUP=$4

PREFIX=${INPUT%.*}
SUFFIX=${INPUT#${INPUT%.*}.}

#----

unset CSVTK_OPT
if [ "${HIST}" = "1" ]; then
    CSVTK_OPT=" --color-index 2"
    OUTPUT=${OUTPUT:-${PREFIX}_hist_F${XCOL}.svg}
    csvtk plot hist "${INPUT}" -f ${XCOL} ${CSVTK_OPT} -o "${OUTPUT}"
else
    if [ "${GROUP}" != "" ]; then
	CSVTK_OPT="${CSVTK_OPT} -g ${GROUP}"
    fi
    if [ "${SCATTER}" = "1" ]; then
	CSVTK_OPT="${CSVTK_OPT} --scatter"
    fi
    OUTPUT=${OUTPUT:-${PREFIX}_2d_X${XCOL}Y${YCOL}.svg}
    csvtk plot line "${INPUT}" -x ${XCOL} -y ${YCOL} ${CSVTK_OPT} -o "${OUTPUT}"
fi

echo "-- ${OUTPUT} was created."

#----
remove_tmpdir
#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

