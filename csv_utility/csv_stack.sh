#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-09-01 17:10:39>
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
check_commands paste

usage_exit() {
    cat <<EOF 2>&1
simply append csv files according to columns or rows.
Usage: $SNAME [-m dir] [-c categories] [-r n] csv_file csv_file [csv_file ...]
options:
  -r n          : number of rows of headers, default=1
  -m dir        : direction of stack, v or h, default=v
  -c categories : name of categories for each csv files, with csv format.
                  this options is available for only vertical mode.
remark:
 when '-c' option was used, number of categories must be equal to nuber of csv files.
 if this option was given, for each record there is column of category in result.

example:
  csv_stack.sh -c p1,p2 test1.csv test2.csv
  A,B,Category
  1,2,p1
  3,4,p1
  5,6,p1
  7,8,p2
  9,10,p2
  11,12,p2
  13,14,p2

EOF
    exit 1
}

while getopts c:m:r:h OPT
do
    case $OPT in
        c)  CATS=$OPTARG
            ;;
        m)  MODE=$OPTARG
            ;;
	r)  HROWS=$OPTARG
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

MODE=${MODE:-v}
HROWS=${HROWS:-1}

INPUTS=("$@")

if [ "${CATS}" != "" ]; then
    CATS=($(echo ${CATS} | tr "," " "))
    if (( ${#INPUTS[@]} != ${#CATS[@]} )) ;then
	echo "--error: number of categories must be equal to number of csv files." 1>&2
	exit 1
    fi
fi
#----

if [ "${MODE}" = "v" ]; then
    COUNT=0
    for f in ${INPUTS[@]}; do
	if [ "${COUNT}" = "0" ]; then
	    if (( "${#CATS[@]}" > 0 ));then
		awk "NR<=${HROWS} {print \$0\",Category\"}; NR>${HROWS} {print \$0\",${CATS[${COUNT}]}\"}" "${f}"
	    else
		cat "${f}"
	    fi
	else
	    if (( "${#CATS[@]}" > 0 ));then
		awk "NR>${HROWS} {print \$0\",${CATS[${COUNT}]}\"}" "${f}"
	    else
		awk "NR>${HROWS} {print}" "${f}"
	    fi
	fi
	COUNT=$((COUNT+1))
    done
elif [ "${MODE}" = "h" ]; then
    paste -d, "${INPUTS[@]}"
else
    echo "--error: invalid mode: ${MODE}" 1>&2
fi



#----
# remove_tmpdir
#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

