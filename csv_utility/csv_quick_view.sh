#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2021 , m.akei
# Time-stamp:   <2021-04-24 20:06:58>
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

usage_exit() {
    cat <<EOF 2>&1
Usage: $SNAME [-s word] csv_file
options:
  -s word: word to search

remark:
  see folloing
  Pretty CSV viewing on the Command Line - Stefaan Lippens inserts content here https://www.stefaanlippens.net/pretty-csv.html
EOF
    exit 1
}

while getopts as:h OPT
do
    case $OPT in
        a)  FLAG_A=1
            ;;
        s)  WORD=$OPTARG
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
INPUT_BASE=$(basename ${INPUT})

PREFIX=${INPUT_BASE%.*}
SUFFIX=${INPUT_BASE#${INPUT_BASE%.*}.}
OUTPUT=${PREFIX}.raw

# INPUT=$(check_and_get_stdin "${INPUT}")

#----

if [ "${WORD}" = "" ]; then
    cat "${INPUT}" |\
	perl -pe 's/((?<=,)|(?<=^)),/ ,/g;' | column -t -s, | less  -F -S -X -K
else
    (head -1 ${INPUT}; sed '1d' "${INPUT}"|grep "${WORD}" )|\
	  perl -pe 's/((?<=,)|(?<=^)),/ ,/g;' | column -t -s, | less  -F -S -X -K
fi

#----
# remove_tmpdir
#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

