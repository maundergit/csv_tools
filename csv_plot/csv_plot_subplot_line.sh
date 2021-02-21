#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2021 , m.akei
# Time-stamp:   <2021-02-19 18:24:26>
#----------------------------------------------------------------------
DTSTMP=$(date +%Y%m%dT%H%M%S)

DDIR=$(dirname $0)
SNAME=$(basename $0)
#DDIR_ABS=$(cd $(dirname ${DDIR}) && pwd)/$(basename $DDIR)
DDIR_ABS=$(realpath ${DDIR})
TMPDIR=/tmp
# TMPDIR=/tmp/${SNAME}.$$


usage_exit() {
    cat <<EOF 2>&1
plot multi-columns in csv file as subplot of line chart
Usage: $SNAME [-o output_html] [-t tile] [-p options_of_csv_plot_line] csv_file key_column plot_colun[,plot_column...]
options:
 -o output_html: default={prefix of input file}.html
 -t title : title of chart
 -p options: options of csv_plot_line.py by string 

example:
  csv_plot_subplot_line.sh -t "a b c" -p "--log_y" test_plot.csv ABC000 ABC001,ABC002,ABC003

EOF
    exit 1
}

while getopts o:p:t:h OPT
do
    case $OPT in
        o)  OUTPUT=$OPTARG
            ;;
        p)  POPT=$OPTARG
            ;;
        t)  TITLE=$OPTARG
            ;;
        h)  usage_exit
            ;;
        \?) usage_exit
            ;;
    esac
done
shift $((OPTIND - 1))

if [ "$3" = "" ];  then
    usage_exit
fi

INPUT=$1
KEY_COLUMN=$2
COLUMNS=$3
INPUT_BASE=$(basename ${INPUT})

PREFIX=${INPUT_BASE%.*}
SUFFIX=${INPUT_BASE#${INPUT_BASE%.*}.}
OUTPUT=${OUTPUT:-${PREFIX}.html}

# INPUT=$(check_and_get_stdin "${INPUT}")

#----
POPT="${POPT} --noautoscale"
TITLE=${TITLE:-""}

csv_meltpivot.py --mode melt --category_name=C ${INPUT} ${KEY_COLUMN} ${COLUMNS} |\
    csv_plot_line.py --output=${OUTPUT} --title="${TITLE}" --facets=C ${POPT} - ${KEY_COLUMN} Value

#----
# remove_tmpdir
#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

