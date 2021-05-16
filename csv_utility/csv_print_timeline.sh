#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2021 , m.akei
# Time-stamp:   <2021-05-14 20:32:00>
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
check_commands plantuml csv_print_html.py csv_print_html_oia.py csv_print_html_tl.py


function make_index_html(){
    cat <<EOF > ${OUTPUT_INDEX}
<?xml version="1.0" encoding="utf-8"?>
<html>
  <head>
    <title>テキスト文書の時系列データとしての初期分析</title>
  </head>
  <body>
    <h1>テキスト文書の時系列データとしての初期分析</h1>
    <hr/>
    入力文書:${INPUT}
    <ul>
      <li>
	<a href="${OUTPUT_HTML}" target="csv_print_html">CSVの表形式表示</a><br/>
	指定オプション:${O_OPTS}
      </li>
      <li>
	<a href="${OUTPUT_TL_SVG}" target="csv_print_html_tl_svg">トピックの時系列表示</a><br/>
	指定オプション:${TL_OPTS}<br/>
	各項目をクリックすることで、指定列まとめ表示の該当箇所を表示
      </li>
      <li>
	<a href="${OUTPUT_OIA_HTML}" target="csv_print_html_oia">指定列のまとめ表示</a><br/>
	指定オプション:${OIA_OPTS}<br/>
	タイトル行をダブルクリックすることで、検索語句等指定可能、またOIA列以外の列をダブルクリックすることで、${OUTPUT_HTML}の該当箇所表示
      </li>
      <li>
	<a href="${OUTPUT_TL_HTML}" target="csv_print_html_tl">タイムライン表示</a><br/>
	指定オプション:${TL_OPTS}
      </li>
    </ul>
    <hr/>
    
    created：${DTSTMP} by ${SNAME}
  </body>
</html>
EOF
    echo "-- ${OUTPUT_INDEX} was created." 1>&2
    echo "   ==========================" 1>&2
    echo "   please open ${OUTPUT_INDEX}" 1>&2
    echo "   ==========================" 1>&2

}
function make_oia_handler(){
    OIA_HANDLER=oia_handler.js
    cat <<EOF > ${OIA_HANDLER}
// -*- coding:utf-8 mode:javascript -*-
// File: oia_handler.js
// Copyright (C) 2021 by m.na.akei 
// Time-stamp: <2021-05-15 17:45:07>

/* exported */

function oia_dblclick_from_td(val_dic){
    let html_url="${OUTPUT_OIA_HML}";
    let nrec= val_dic["nrec"]; // record number in csv
    let id_in_html="rid_"+nrec;
    let url=html_url+"#"+id_in_html;
    window.open(url,"__blank");
    
}

//-------------
// Local Variables:
// mode: javascript
// coding: utf-8-unix
// End:

EOF
    echo "-- ${OIA_HANDLER} was created" 1>&2
}
function triming_svg(){
    echo "-- triming: ${OUTPUT_TL_SVG}" 1>&2
    TMP_SVG=${SNAME}_$$.svg
    cp ${OUTPUT_TL_SVG} ${TMP_SVG}
    SED_SCR=
    while read LINE; do
	if [ "${LINE:0:1}" = "#" ]; then
	    continue
	fi
	if [ "${#LINE}" = "0" ]; then
	    continue
	fi
	CVS=(${LINE})
	IDX=${CVS[0]}
	RID="rid_${IDX}"
	WORD=${CVS[1]}
	SED_SCR="${SED_SCR}s/>${WORD}</><a href=\"${OUTPUT_OIA_HTML}#${RID}\" target=\"_blank\">${WORD}<\/a></g;"
    done < <((sed '1d' ${OUTPUT_TAGS_TEXT}|sed 's/,/ /g');echo -e "\n")
    SED_SCR="${SED_SCR}s/<\/g><\/svg>/<\/g><style type='text\/css'>a:hover {font-weight:bold;font-size:110%;}<\/style><\/svg>/;"
    sed "${SED_SCR}" ${OUTPUT_TL_SVG} ${TMP_SVG} > ${OUTPUT_TL_SVG}
    rm ${TMP_SVG}
}

usage_exit() {
    cat <<EOF 2>&1
テキスト文書の時系列データとしての初期分析用ツール
Usage: ${SNAME} [optins]  csv_file datetime_column observation_column [investigation_column [action_column]]
options:
  -a columns: "指定列のまとめ表示"における追加表示列、ここで指定した列は先頭列に表示される
  -c part_color: 強調表示する指定語句,正規表現が指定可能
  -d datetime_format: 時刻列の書式
  -m module_figure_option: タイムライン表示に表示される図面情報
  -p words_map_file: タイムライン表示に表示される図面情報と指定語句の対応関係を指定するテキストファイル

  '-a'については'csv_print_html_oia.py --help'の'--columns'の項を参照のこと
  '-c'については'csv_print_html.py --help'又は'csv_print_html_oia.py --help'の'--part_color'の項を参照のこと
  '-d','-m','-p'については'csv_print_html_tl.py --help'の'--datetime_format'、'--module_figure'、'--words_map'の項を参照のこと

remark:
  このツールは、以下のツール群を一括適用するためのシェルスクリプトです。
  各ツールで生成されるHTML、SVG間のハイパーリンクを設定し、相互に行き来することを可能とします。
  csv_print_html.py,csv_print_html_oia.py,csv_print_html_tl.py

  'oia_handler.js'を修正することで"指定列のまとめ表示"からのリンクジャンプ先を制御可能です。

example 
  csv_print_timeline.sh -c "吾輩,人間,我慢,書斎" wagahaiwa_nekodearu.csv date contente content
  csv_print_timeline.sh -c "吾輩,人間,我慢,書斎" -m "wagahaiwa_nekodearu_module.svg:7" -p wagahaiwa_nekodearu_map.txt wagahaiwa_nekodearu.csv date content
  csv_print_timeline.sh -a IDX,B,C -c 'this:red' test3.csv  DT O I A


EOF
    exit 1
}

while getopts a:c:d:m:p:h OPT
do
    case $OPT in
        a)  ACOLUMNS=${OPTARG}
            ;;
        c)  PART_COLOR=$OPTARG
            ;;
        d)  DATETIME_FORMAT=$OPTARG
            ;;
        m)  MODULE_TL=$OPTARG
            ;;
        p)  MAP_TL_TEXT=$OPTARG
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
INPUT_BASE=$(basename ${INPUT})

DATE_COL=$2
O_COL=$3
I_COL=$4
A_COL=$5

PREFIX=${INPUT_BASE%.*}
SUFFIX=${INPUT_BASE#${INPUT_BASE%.*}.}

OUTPUT_INDEX=${PREFIX}_index.html
OUTPUT_HTML=${PREFIX}.html
OUTPUT_OIA_HTML=${PREFIX}_oia.html
OUTPUT_TL_HTML=${PREFIX}_tl.html
OUTPUT_TAGS_TEXT=${PREFIX}_tl_gantt_tags.csv
OUTPUT_TL_PU=${PREFIX}_tl.pu
OUTPUT_TL_SVG=${PREFIX}_tl.svg

# INPUT=$(check_and_get_stdin "${INPUT}")

#----

DATE_FORMAT=${DATE_FORMAT:-%Y-%m-%d %H:%M:%S}

O_OPTS=
OIA_OPTS=
TL_OPTS=
if [ "${ACOLUMNS}" != "" ]; then
    OIA_OPTS="${OIA_OPTS} --columns=${ACOLUMNS}"
    TL_OPTS="${TL_OPTS} --columns=${DATE_COL},${ACOLUMNS}"
else
    TL_OPTS="${TL_OPTS} --columns=${DATE_COL}"
fi
if [ "${PART_COLOR}" != "" ]; then
    O_OPTS="${O_OPTS} --part_color=${PART_COLOR}"
    OIA_OPTS="${OIA_OPTS} --part_color=${PART_COLOR}"
    TL_OPTS="${TL_OPTS} --part_color=${PART_COLOR} --group_by_part_color"
fi
if [ "${MODULE_TL}" != "" ]; then
    TL_OPTS="${TL_OPTS} --module_figure=${MODULE_TL}"
fi
if [ "${MAP_TL_TEXT}" != "" ]; then
    TL_OPTS="${TL_OPTS} --words_map=${MAP_TL_TEXT}"
fi

echo -e "\n-- csv_print_html" 1>&2
csv_print_html.py ${O_OPTS} --search_on_html ${INPUT} > ${OUTPUT_HTML}
if [ "$?" != "0" ]; then
    exit
fi

echo -e "\n-- csv_print_html_oia" 1>&2
csv_print_html_oia.py ${OIA_OPTS} --search_on_html ${INPUT}  ${O_COL} ${I_COL} ${A_COL} > ${OUTPUT_OIA_HTML}
if [ "$?" != "0" ]; then
    exit
fi

echo -e "\n-- csv_print_html_tl" 1>&2
csv_print_html_tl.py ${TL_OPTS} --datetime_format="${DATE_FORMAT}" --output=${OUTPUT_TL_HTML}\
		     ${INPUT} ${DATE_COL} ${O_COL} ${I_COL} ${A_COL}
if [ "$?" != "0" ]; then
    exit
fi

echo -e "\n-- convert plantuml to SVG: ${OUTPUT_TL_SVG}" 1>&2
plantuml -tsvg ${OUTPUT_TL_PU}
if [ "$?" != "0" ]; then
    cat <<EOF 2>&1
??error: latest version of plantuml is required.
EOF
    exit
fi

triming_svg
make_oia_handler
make_index_html


#----
# remove_tmpdir
#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

