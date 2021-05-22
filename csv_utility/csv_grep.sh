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
Usage: $SNAME [-c columns] [-i] [-m] patterns csv_file
options:
  -c columns: columns where patternwas searched. 
  -i        : invert match
  -m        : multipattern mode

remark:
  with '-m', some patterns with csv format are available. then results for each pattern will be merged.

example:
  csv_grep.sh -c COL_0006 "PAT\d+3" big_sample_arb.csv |csvcut -c COL_0006 | less
  csv_grep.sh -c COL_0006 -m "PAT\d+3,PAT\d+4" big_sample_arb.csv |csvcut -c COL_0006 | less

EOF
    exit 1
}

while getopts ic:mh OPT
do
    case $OPT in
        i)  INVERT=1
            ;;
        c)  COLUMNS=$OPTARG
            ;;
        m)  MULTI_PATTERNS=1
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
    echo "-- invert match mode" 1>&2
fi

if [ "${MULTI_PATTERNS}" = "" ]; then
    PATS=(${PATTERN})
    echo "-- single-pattern mode: ${PATS[@]}" 1>&2
else
    PATS=($(echo "${PATTERN}" | csvformat -D" "))
    echo "-- multi-pattern mode: ${PATS[@]}" 1>&2
fi

function do_grep(){
    PATTERN=$1
    if [ "${COLUMNS}" != "" ]; then
	OIFS=${IFS}
	IFS=\|
	CS=($(echo "${COLUMNS}" | sed "s/\r//g" | tr "," "|"))
	IFS=${OIFS}
	for C in ${CS[@]}; do
	    csvgrep ${G_OPTS} --columns ${C} --regex "${PATTERN}" "${INPUT}" | sed '1d'
	    csvgrep ${G_OPTS} --columns ${C} --regex "${PATTERN}" "${INPUT}" | sed '1d'
	done | sort | uniq 
    else
	grep ${G_OPTS} -P "${PATTERN}" "${INPUT}"
    fi
}
function do_grep_xsv(){
    PATTERN=$1
    if [ "${COLUMNS}" != "" ]; then
	xsv search --select ${COLUMNS} ${G_OPTS} "${PATTERN}" "${INPUT}" | sed '1d'
    else
	xsv search ${G_OPTS} "${PATTERN}" "${INPUT}" | sed '1d'
    fi
}

ACOLUMNS=${COLUMNS}
(head -1 "${INPUT}")
COLUMNS=${ACOLUMNS}

if [ "$(which xsv)" = "" ]; then
    GREP_MODE=csvgrep/grep
else
    GREP_MODE=xsv
fi
echo "-- grep mode: ${GREP_MODE}" 1>&2
for P in ${PATS[@]}; do
    echo "-- processing pattern: ${P}" 1>&2
    if [ "${GREP_MODE}" = "xsv" ]; then
	do_grep_xsv ${P}
    else
	do_grep ${P}
    fi
done | sort | uniq

#----
remove_tmpdir
#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

