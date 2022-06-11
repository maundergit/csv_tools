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

check_os () {
    OSNAME=$(uname -o 2>/dev/null || echo others)
    OSVER=$(uname -a 2>/dev/null)   # -r or -v
    if [ "${OSNAME}" = "GNU/Linux" ]; then
        if [[ "${OSVER}" =~ microsoft ]]; then
            echo something to do for WSL
        else
            echo something to do for linux other than WSL
        fi
        echo something to do for linux
    else
        echo something to do for others
    fi
}
check_xwindow() {
    if [ "$DISPLAY" = "" ]; then
        echo "-- error: 'DISPLAY' environment was not definded." >&2
        exit 1
    fi
    if [ "$(xset q 2>/dev/null)" = "" ]; then
        echo "-- error: No X server at \$DISPLAY [$DISPLAY]" >&2
        exit 1
    fi
}
check_do() {
    MODE=$1
    CHK_CMD=$2
    shift
    CMD="$@"
    unset MES
    if [ "$(which ${CHK_CMD})" = "" ]; then
        if [ "${MODE}" = "0" ]; then
            echo "-- warning: not found ${CHK_CMD}"
        else
            echo "-- error: not found ${CHK_CMD}"
            exit 1;
        fi
    else
        ${CMD}
    fi
}
change_stdout(){
    F=$@
    exec 1<&-     # close stdout
    exec 1<>${F}  # reopen stdout as ${F} for read and write
    # exec 2<&-   # close stderr
    # exec 2>&1   # reopen 
}
check_commands_and_install() {
    # usage: check_commands_and_install "${array[@]}"
    CHK_CMDS=("$@")
    unset MES
    for c in "${CHK_CMDS[@]}"; do
        if [ "$(which ${c})" = "" ]; then
            if [ -x /usr/lib/command-not-found ]; then
                APT_CMD=$(/usr/lib/command-not-found -- "$c" 2>&1 | awk '/^(sudo|apt)/ {print $0}')
                ${APT_CMD}
            elif [ -x /usr/share/command-not-found/command-not-found ]; then
                APT_CMD=$(/usr/share/command-not-found -- "$c" 2>&1 | awk '/^(sudo|apt)/ {print $0}')
                ${APT_CMD}
            else
                MES="${MES}-- error: not found $c\n"
            fi
        fi
    done
    if [ "${MES}" != "" ]; then
        echo -e "${MES}" 1>&2
        exit 1
    fi
}
get_absolutepath() {
    P=$1
    RES=$(cd $(dirname ${P}) && pwd)/$(basename ${P})
    echo ${RES}
}
print_array(){
    # bash - How to pass an array as function argument? - Ask Ubuntu https://askubuntu.com/questions/674333/how-to-pass-an-array-as-function-argument
    # usage: print_array "${array[@]}"
    local A
    A=("$@")
    for v in "${A[@]}"; do
        echo "'$v'"
    done
}
function stderr_out(){
    MESSAGES=("$@")
    for m in "${MESSAGES[@]}"; do
	echo "${m}" 1>&2
    done
}
unused_port(){
    # usage: unused_port star_port [end_port]
    SP=$1
    EP=${2:-$((${SP}+10))}
    PS=($(nc -v -z 127.0.0.1 ${SP}-${EP} 2>&1 | awk '/failed/ {print $6}'))
    if (( ${#PS[@]} > 0)); then
	echo "${PS[0]}"
    else
	echo "??error:unused_port: unused port was not found in ${SP}-${EP}" 1>&2
	exit 1
    fi
}

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

