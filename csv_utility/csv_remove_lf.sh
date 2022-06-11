#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2022 , m.akei
# Time-stamp:   <2022-06-11 13:00:44>
#----------------------------------------------------------------------
DTSTMP=$(date +%Y%m%dT%H%M%S)

DDIR=$(dirname $0)
SNAME=$(basename $0)
#DDIR_ABS=$(cd $(dirname ${DDIR}) && pwd)/$(basename $DDIR)
DDIR_ABS=$(realpath ${DDIR})
TMPDIR=/tmp
# TMPDIR=/tmp/${SNAME}.$$


#---- 
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

usage_exit() {
    cat <<EOF 2>&1
to remove CR/LF in value of each cell.
Usage: $SNAME [-r str] csv_file column [columns [...]]
options:
  -r str : string instead of CR/LF.
example:
  ${SNAME} test.csv A B
  ${SNAME} -r "/" test.csv A B
EOF
    exit 1
}
check_commands csv_uty.py

while getopts r:h OPT
do
    case $OPT in
        r)  DEST=$OPTARG
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
shift
COLUMNS=($@)

PREFIX=${INPUT_BASE%.*}
SUFFIX=${INPUT_BASE#${INPUT_BASE%.*}.}
OUTPUT=${PREFIX}_nocrlf.csv

# INPUT=$(check_and_get_stdin "${INPUT}")

#----

CNS=${COLUMNS[@]}

ADD_OPTS=()
for CN in ${CNS[@]}; do
    NCN="${CN}_NOCRNF"
    ADD_OPTS=(${ADD_OPTS[@]} "${NCN}=\${${CN}}.str.replace(r\"[\r\n]+\"\,\"${DEST}\"\,regex=True)")
    # echo "${ADD_OPTS[@]}"
done
AOPTS=
for v in ${ADD_OPTS[@]}; do
    AOPTS="$AOPTS,$v"
done
AOPTS=${AOPTS#,}
#echo $AOPTS
csv_uty.py --add_columns="${AOPTS}" "${INPUT}"

#----
# remove_tmpdir
#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

