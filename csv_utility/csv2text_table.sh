#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2021 , m.akei
# Time-stamp:   <2021-06-13 17:05:22>
#----------------------------------------------------------------------
DTSTMP=$(date +%Y%m%dT%H%M%S)

DDIR=$(dirname $0)
SNAME=$(basename $0)
#DDIR_ABS=$(cd $(dirname ${DDIR}) && pwd)/$(basename $DDIR)
DDIR_ABS=$(realpath ${DDIR})
# TMPDIR=/tmp
TMPDIR=/tmp/${SNAME}.$$

#---- 
remove_tmpdir(){
    if [[ "${TMPDIR}" != "" && "${TMPDIR}" =~ ${SNAME} && -e "${TMPDIR}" ]]; then
	rm -rf "${TMPDIR}"
    fi
}
make_tmpfile(){
    ID=$1
    if [[ "${TMPDIR}" != "" && ! -e "${TMPDIR}" ]]; then
	mkdir "${TMPDIR}"
    fi
    FN="${TMPDIR}/${ID}_$$.tmp"
    echo "${FN}"
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
# check_commands tabulate

usage_exit() {
    cat <<EOF 2>&1
print csv data with ascii character.
Usage: $SNAME [-f otuput_format] csv_file
options:
  -f output_format: default=orgtbl
                    availabl format:
                    plain, simple, grid, fancy_grid, pipe, orgtbl,
		    rst, mediawiki, html, latex, latex_raw,
		    latex_booktabs, latex_longtable, tsv

remark:
  'tabulate' is required.
  astanin/python-tabulate- https://github.com/astanin/python-tabulate

example:
  ${SNAME} -f orgtbl test.csv | sed -E '2s/\+-/|-/g'  # markdown format

EOF
    exit 1
}

while getopts af:h OPT
do
    case $OPT in
        a)  FLAG_A=1
            ;;
        f)  OUTPUT_FORMAT=$OPTARG
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

INPUT=$(check_and_get_stdin "${INPUT}")

#----

OUTPUT_FORMAT=${OUTPUT_FORMAT:-orgtbl}

CHK_1=$(which csvlook)
CHK_2=$(which tabulate)

if [ "${CHK_2}" != "" ]; then
    tabulate -s, --header --format ${OUTPUT_FORMAT} ${INPUT}
elif [ "${CHK_1}" != "" ]; then
    echo "#warn:${SNAME}:tabulate was not found. So '-f' is ignored." 1>&2
    # convert to orgtbl format
    csvlook --no-inference --blank ${INPUT} | sed '2s/ \| -/ + -/g;2s/ /-/g;'
else
    echo "??error:${SNAME}: both csvlook and tabulate were not found." 1>&2
fi

#----
remove_tmpdir
#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:
