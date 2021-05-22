#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-08-16 10:55:08>
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
function stderr_out(){
    MESSAGES=("$@")
    for m in "${MESSAGES[@]}"; do
	echo "${m}" 1>&2
    done
}

check_commands csvlook seq awk sed

usage_exit() {
    cat <<EOF 2>&1
print range of rows and range of columns in csv file
Usage: $SNAME [-i] csv_file range_of_rows range_of_columns
arguments:
  csv_file        : csv file
  range_of_rows   : range of rows to print with csv format, 1-base
                    alse keyword 'all' is availabe.
                    ex. 10,20 10,+10 all
  range_of_columns: range of columns to print with csv format, 1-base
                    also name of column or 'all' is available.
                    ex. 10,20 10,+10 CO_0000,COL_0002

options:
  -i :add index column

example:
  csv_cut.sh -i big_sample_int.csv 100,+3 1000,+3|csvlook -I
  -- range of rows   : 100-103
  -- range of columns: 1000-1003
  | index | COL_0999 | COL_1000 | COL_1001 | COL_1002 |
  | ----- | -------- | -------- | -------- | -------- |
  | 100   | 111483   | 111484   | 111485   | 111486   |
  | 101   | 112599   | 112600   | 112601   | 112602   |
  | 102   | 113715   | 113716   | 113717   | 113718   |
  | 103   | 114831   | 114832   | 114833   | 114834   |

  csv_cut.sh -i big_sample_int.csv 100,+3 500,+3|csvtool transpose -|csvlook -I
  -- range of rows   : 100-103
  -- range of columns: 500-503
  | index    | 100    | 101    | 102    | 103    |
  | -------- | ------ | ------ | ------ | ------ |
  | COL_0499 | 110983 | 112099 | 113215 | 114331 |
  | COL_0500 | 110984 | 112100 | 113216 | 114332 |
  | COL_0501 | 110985 | 112101 | 113217 | 114333 |
  | COL_0502 | 110986 | 112102 | 113218 | 114334 |
EOF
    exit 1
}

while getopts ih OPT
do
    case $OPT in
	i) INDEX=1
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

R_RANGE=$2
C_RANGE=$3

if [ "${INPUT}" = "-" ]; then
    TMPFILE="${TMPDIR}/${SNAME}_input.tmp"
    cat > ${TMPFILE}
    INPUT=${TMPFILE}
elif [ ! -e "${INPUT}" ]; then
    echo "??Error: file not found: ${INPUT}" 1>&2
    exit 1
fi
if [ "${R_RANGE}" = "all" -a "${C_RANGE}" = "all" ]; then
    echo "??Error: range_of_rows and range_of_colums can not become 'all' at the same time." 1>&2
    exit
fi

function get_column_index(){
    CIDX=$1
    shift
    HS=("$@")
    if [[ ${CIDX} =~ ^[0-9]+$ ]]; then
	echo "${CIDX}"
	return
    else
	for (( i=0; i<${#HS[@]}; i++)); do
	    if [ "${HS[$i]}" = "${CIDX}" ];then
		echo "$((i+1))"
		return
	    fi
	done
    fi
    echo "??Error: columnname:${CIDX} not found" 1>&2
}

#----
if [ "$(which xsv)" != "" ]; then
    echo "#warn:csv_stack.sh:you have 'xsv', using 'xsv select' is recomended." 1>&2
fi
if [ "${R_RANGE}" != "all" ]; then
    RS=($(echo ${R_RANGE}| tr "," " "))
    R0=${RS[0]}
    if [[ ${#RS[@]} == 1 ]]; then
	R1=${R0}
	SROW="${R0}"
    else
	if [ "${RS[1]:0:1}" = "+" ]; then
	    R1=$((${R0}${RS[1]}))
	elif [ "${RS[1]:0:1}" = "-" ]; then
	    R0=$((${R0}${RS[1]}))
	    R1=${RS[0]}
	else
	    R1=${RS[1]}
	fi
	SROW="${R0}-${R1}"
    fi
else
    R0="all"
    SROW="all"
fi

if [ "${C_RANGE}" != "all" ]; then
    OIFS=${IFS}
    IFS=\|
    HEADERS=($(awk 'NR==1 {print $0}' "${INPUT}" | sed "s/\r//g" | tr "," "|"))
    IFS=${OIFS}
    
    CS=($(echo ${C_RANGE}| tr "," " "))
    C0=${CS[0]}
    C0=$(get_column_index "${C0}" "${HEADERS[@]}")
    if [ "${C0}" = "" ]; then exit 1; fi
    if [[ ${#CS[@]} == 1 ]];then
	SCOL=${C0}
    else
	if [ "${CS[1]:0:1}" = "+" ]; then
	    C1=$(get_column_index "${CS[1]:1}" "${HEADERS[@]}")
	    if [ "${C1}" = "" ]; then exit 1; fi
	    C1=$((${C0}+${C1}))
	elif [ "${CS[1]:0:1}" = "-" ]; then
	    C1=$(get_column_index "${CS[1]:1}" "${HEADERS[@]}")
	    if [ "${C1}" = "" ]; then exit 1; fi
	    C0=$((${C0}-${C1}))
	    C1=${C1}
	else
	    C1=$(get_column_index "${CS[1]}" "${HEADERS[@]}")
	    if [ "${C1}" = "" ]; then exit 1; fi
	fi
	SCOL="${C0}-${C1}"
    fi
else
    C0="all"
    SCOL="all"
fi
stderr_out "$(cat <<EOF
-- range of rows   : ${SROW}
-- range of columns: ${SCOL}
EOF
)"

if [ "${R0}" != "all" -a "${C0}" != "all" ]; then
    R0=$((R0+1))
    R1=$((R1+1))
    RES=$(csvcut --columns ${SCOL} "${INPUT}" | awk "NR==1 || NR>=${R0} && NR<=${R1} {print \$0}")
elif [ "${R0}" = "all" ]; then
    RES=$(csvcut --columns ${SCOL} "${INPUT}")
elif [ "${C0}" = "all" ]; then
    R0=$((R0+1))
    R1=$((R1+1))
    RES=$(awk "NR==1 || NR>=${R0} && NR<=${R1} {print \$0}" "${INPUT}")
fi
if [ "${INDEX}" = "1" ]; then
    TMPFILE=csv_cut_$$.txt
    (echo "index";seq $((R0-1)) $((R1-1)) ) > ${TMPFILE}
    echo "${RES}" | paste -d, ${TMPFILE} -
    rm -f ${TMPFILE}
else
    echo "${RES}"
fi

if [ "${TMPFILE}" != "" -a -e "${TMPFILE}" ]; then
    rm -f ${TMPFILE}
fi

#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

