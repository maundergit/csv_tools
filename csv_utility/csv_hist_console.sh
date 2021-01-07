#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-08-22 14:12:43>
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
check_commands jp

usage_exit() {
    cat <<EOF 2>&1
plot histogram by ascii character.
Usage: $SNAME [-p] [-s] [-d] [-l] csv_file X_column [y_column]
arguments:
  csv_file : path of csv file
  x_column : column index of x, 0-base
  y_column : column index of y, 0-base
options:
  -p      : line plot, y_column is required.
  -s      : scatter plot, y_column is required.
  -d      : heat map plot, y_column is required.
  -l      : histogram, y_column is not required.
  -b bins : number of bins for '-d' and '-l', default=20 

remark:
 at least one of '-p', '-s', '-d', '-l' must be given.
 GitHub - sgreben/jp: dead simple terminal plots from JSON data. single binary, no dependencies. linux, osx, windows. 
  https://github.com/sgreben/jp

example:
   csv_hist_console.sh -l test_plot.csv 1

EOF
    exit 1
}

while getopts psdlb:h OPT
do
    case $OPT in
	b)  BINS=$OPTARG
	    ;;
        p)  PLOT=1
            ;;
        s)  SCATTER=1
            ;;
        d)  HIST2D=1
            ;;
        l)  HIST=1
            ;;
        h)  usage_exit
            ;;
        \?) usage_exit
            ;;
    esac
done
shift $((OPTIND - 1))

if [ "$2" = "" ];  then
    usage_exit
fi

JP="jp"

INPUT=$1
if [ "${INPUT}" = "-" ]; then
    TMPFILE="${TMPDIR}/${SNAME}_input.tmp"
    cat > ${TMPFILE}
    INPUT=${TMPFILE}
elif [ ! -e "${INPUT}" ]; then
    echo "??Error: file not found: ${INPUT}" 1>&2
    exit 1
fi

X_COLUMN=$2
Y_COLUMN=$3
if [[ ( "${PLOT}" = "1" || "${SCATTER}" = "1" || "${HIST2D}" = "1" ) && "${Y_COLUMN}" = "" ]]; then
    echo "--error: y_column is required with '-p' or '-s', '-d'"
    exit 1
fi

XYARG="[*][${X_COLUMN},${Y_COLUMN}]"
XARG="[*][${X_COLUMN}]"
BINS=${BINS:-20}
HIST_OPT="-bins ${BINS}"
#----

CHK=0
# line plot
if [ "${PLOT}" = "1" ]; then
    CHK=1
     "${JP}" -input csv -xy "${XYARG}" < "${INPUT}"
     if [ "${SCATTER}" = "1" -o "${HIST2D}" = "1" -o "${HIST}" = "1" ]; then
	 read -p "return to continue:" ans
     fi
fi

# scatter plot
if [ "${SCATTER}" = "1" ]; then
    CHK=1
    "${JP}" -input csv  -xy "${XYARG}" -type scatter < "${INPUT}"
    if [ "${HIST2D}" = "1" -o "${HIST}" = "1" ]; then
	read -p "return to continue:" ans
    fi
fi

# hist 2d
if [ "${HIST2D}" = "1" ]; then
    CHK=1
    "${JP}" -input csv  -xy "${XYARG}" -type hist2d -canvas full-bw ${HIST_OPT} < "${INPUT}"
    if [ "${HIST}" = "1" ]; then
	read -p "return to continue:" ans
    fi
fi

# hist
if [ "${HIST}" = "1" ]; then
    CHK=1
    "${JP}" -input csv  -xy "${XARG}" -type hist ${HIST_OPT} < "${INPUT}"
    # echo "${JP}" -input csv  -xy "${XARG}" -type hist ${HIST_OPT} ${INPUT}
fi

if [ "${CHK}" = "0" ]; then
    echo "--error: any of '-p','-s','-d','-l' was not given." 1>&2
fi

if [ "${TMPFILE}" != "" -a -e "${TMPFILE}" ]; then
    rm -f ${TMPFILE}
fi

#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

