#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-08-17 19:04:31>
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
check_commands awk sed

usage_exit() {
    cat <<EOF 2>&1
to get index of column  or name of column with 1-base,
Usage: $SNAME csv_file column_name_or_index

EOF
    exit 1
}

while getopts ad:h OPT
do
    case $OPT in
        a)  FLAG_A=1
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

if [ "$2" = "" ];  then
    usage_exit
fi

INPUT=$1
COLNAME=$2

if [ "${INPUT}" = "-" ]; then
    TMPFILE="${TMPDIR}/${SNAME}_input.tmp"
    cat > ${TMPFILE}
    INPUT=${TMPFILE}
elif [ ! -e "${INPUT}" ]; then
    echo "??Error: file not found: ${INPUT}" 1>&2
    exit 1
fi

function get_column_index(){
    CIDX=$1
    shift
    HS=("$@")
    if [[ ${CIDX} =~ ^[0-9]+$ ]]; then
	echo "${CIDX}"
    else
	for (( i=0; i<${#HS[@]}; i++)); do
	    if [ "${HS[$i]}" = "${CIDX}" ];then
		echo "$((i+1))"
		break
	    fi
	done
    fi
}
#----

OIFS=${IFS}
IFS=\|
HEADERS=($(awk 'NR==1 {print $0}' "${INPUT}" | sed "s/\r//g" | tr "," "|"))
IFS=${OIFS}

if [[ ${COLNAME} =~ ^[0-9]+$ ]]; then
    COLNAME=$((COLNAME-1))
    C0=${HEADERS[${COLNAME}]}
else
    C0=$(get_column_index "${COLNAME}" "${HEADERS[@]}")
fi
echo ${C0}

if [ "${TMPFILE}" != "" -a -e "${TMPFILE}" ]; then
    rm -f ${TMPFILE}
fi

#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

