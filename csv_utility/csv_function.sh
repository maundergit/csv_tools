#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-08-23 10:07:22>
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
function bin2dec(){
    x2dec
    cat <<'EOF'
BASE=2
x2dec "$@"
EOF
}
function oct2dec(){
    x2dec
    cat <<'EOF'
BASE=8
x2dec "$@"
EOF
}
function hex2dec(){
    x2dec
    cat <<'EOF'
BASE=16
x2dec "$@"
EOF
}
function x2dec(){
    cat <<'EOF'
function x2dec(){
    INS=("${@}")
    RES=""

    for v in ${INS[@]}; do
	if [[ ${v} =~ [^0-9] ]]; then
	    RES="${RES}${v},"
	else
	    RES="${RES}$((${BASE}#${v})),"
	fi
    done

    if [[ ${#RES} == 0 ]]; then
	echo "${INS[@]}"
    else
	RES=${RES::-1}
	echo "${RES}"
    fi
}
EOF
}

function dec2bin(){
    dec2x
    cat <<'EOF'
BASE=2
dec2x "$@"
EOF
}
function dec2oct(){
    dec2x
    cat <<'EOF'
BASE=8
dec2x "$@"
EOF
}
function dec2hex(){
    dec2x
    cat <<'EOF'
BASE=2
dec2x "$@"
EOF
}
function dec2x(){
    cat <<'EOF'
function dec2x(){
    INS=("${@}")
    RES=""

    for v in ${INS[@]}; do
	if [[ ${v} =~ [^0-9] ]]; then
	    RES="${RES}${v},"
	else
	    v=$(echo "obase=${BASE};${v}" | bc)
	    RES="${RES}${v},"
	fi
    done

    if [[ ${#RES} == 0 ]]; then
	echo "${INS[@]}"
    else
	RES=${RES::-1}
	echo "${RES}"
    fi
}
EOF
}
function print_list_functions(){
    cat <<'EOF'
== available implicit functions:
bin2dec   : binary string to decimal
oct2dec   : octet string to decimal
hex2dec   : hex string to decimal
dec2bin   : decimal to binary string
dec2oct   : decimal to octet string
dec2hex   : decimal to hex string

EOF
}

check_commands csvtool

usage_exit() {
    cat <<EOF 2>&1
replace contents of columns with values that were processed by 'function'.
Usage: $SNAME [-a suffix] csv_file columns function_name
Usage: $SNAME -l

arguments:
  csv_file      : path of csv file
  columns       : columns to apply function,1-base, ex. 1-2,3 
  function_name : program or npath of shell script or implicit function(see '-l')

options:
  -l: print available implicit function
  -a suffix: append mode, suffix is used for new columnm name.

EOF
    cat <<'EOF' 2>&1
remark:
  program or script has each value of columns as arguments, 
  and write results with csv format, that has same number of fileds.

  sample of script(bin2dec):
       INS=("${@}")
       RES=""
       BASE=2
       for v in ${INS[@]}; do
           if [[ ${v} =~ [^0-9] ]]; then
	   	RES="${RES}${v},"
           else
	    	RES="${RES}$((${BASE}#${v})),"
           fi
       done

       if [[ ${#RES} == 0 ]]; then
           echo "${INS[@]}"
       else
           RES=${RES::-1}
           echo "${RES}"
       fi

example:
 csv_function.sh test.csv 1 bin2dec

 input:
 A,B
 10,01
 11,10

 output:
 A,B
 2,01
 3,10

EOF
    exit 1
}

while getopts a:ld:h OPT
do
    case $OPT in
	a)  APPEND_MODE=$OPTARG
	    ;;
        l)  LIST_FUNCTIONS=1
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

if [ "${LIST_FUNCTIONS}" = "1" ]; then
    print_list_functions
    exit 0
fi
if [ "$3" = "" ];  then
    usage_exit
fi

INPUT=$1
COLUMNS=$2
FUNC_NAME=$3

if [[ "$(type -t ${FUNC_NAME} )" != "function" && ( ! -e "${FUNC_NAME}" || ! -x "${FUNC_NAME}" ) ]]; then
    echo "-- function was not found or was not executable: ${FUNC_NAME}" 1>&2
    exit 1
fi

PREFIX=${INPUT%.*}
SUFFIX=${INPUT#${INPUT%.*}.}
OUTPUT=${PREFIX}_function.csv

#----

TRIMED_CSV_FILE="/tmp/csv_function_trimed_$$.csv"

# trim empty cells at bottom
csvtool trim b ${INPUT} > ${TRIMED_CSV_FILE}

if [[ "$(type -t ${FUNC_NAME} )" == "function" ]]; then
    SRC_FILE="/tmp/csv_function_$$.sh"
    ${FUNC_NAME} > "${SRC_FILE}"
    chmod u+rx "${SRC_FILE}"
else
    SRC_FILE=${FUNC_NAME}
fi

ROWS0=$(csvtool height "${TRIMED_CSV_FILE}")
COLS="$(csvtool col ${COLUMNS} ${TRIMED_CSV_FILE}| csvtool call ${SRC_FILE} -)"
if [ "${APPEND_MODE}" != "" ]; then
    OIFS=${IFS}
    IFS=\|
    HEADERS=($(echo "${COLS}" |head -1 | tr "," "|"))
    IFS=${OIFS}
    H=;for h in "${HEADERS[@]}"; do H="${H}${h}_${APPEND_MODE},"; done; H=${H::-1}
    echo "${COLS}" | awk -F, "NR==1 {print \"${H}\"}; NR>1 {print}"|csvtool setrows ${ROWS0} -  | paste -d, ${TRIMED_CSV_FILE} - #> ${OUTPUT}
else
    echo "${COLS}" |csvtool setrows ${ROWS0} -  | csvtool pastecol ${COLUMNS} 1- ${TRIMED_CSV_FILE} - #> ${OUTPUT}
fi

if [[ "$(type -t ${FUNCNAME} )" == "function" ]]; then
    rm ${SRC_FILE}
fi
rm ${TRIMED_CSV_FILE}

#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

