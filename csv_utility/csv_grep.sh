#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2021 , m.akei
# Time-stamp:   <2021-05-20 19:25:51>
#----------------------------------------------------------------------
DTSTMP=$(date +%Y%m%dT%H%M%S)

DDIR=$(dirname $0)
SNAME=$(basename $0)
#DDIR_ABS=$(cd $(dirname ${DDIR}) && pwd)/$(basename $DDIR)
DDIR_ABS=$(realpath ${DDIR})
#TMPDIR=/tmp
TMPDIR=/tmp/${SNAME}.$$

remove_tmpdir(){
    if [[ "${TMPDIR}" != "" && "${TMPDIR}" =~ ${SNAME} && -e "${TMPDIR}" ]]; then
	rm -rf "${TMPDIR}"
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
check_commands csvgrep

usage_exit() {
    cat <<EOF 2>&1
grep for csv with regex
Usage: $SNAME [-c columns] [-i] pattern csv_file
options:
  -c columns: columns where patternwas searched. 
  -i        : invert match
EOF
    exit 1
}

while getopts ic:h OPT
do
    case $OPT in
        i)  INVERT=1
            ;;
        c)  COLUMNS=$OPTARG
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

PATTERN=$1
INPUT=$2
INPUT_BASE=$(basename ${INPUT})

INPUT=$(check_and_get_stdin "${INPUT}")

#----
G_OPTS=
if [ "${INVERT}" != "" ]; then
    G_OPTS="--invert-match"
fi

if [ "${COLUMNS}" != "" ]; then
    OIFS=${IFS}
    IFS=\|
    CS=($(echo "${COLUMNS}" | sed "s/\r//g" | tr "," "|"))
    IFS=${OIFS}
    head -1 ${INPUT}
    for C in ${CS[@]}; do
	csvgrep ${G_OPTS} --columns ${C} --regex "${PATTERN}" "${INPUT}" | sed '1d'
    done | sort | uniq 
else
    head -1 "${INPUT}"
    grep ${G_OPTS} -P "${PATTERN}" "${INPUT}"
fi

#----
remove_tmpdir
#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

