#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_print_html_oia.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2021 by m.na.akei
# Time-stamp:   <2021-04-25 16:33:53>
# Licence:
# ----------------------------------------------------------------------
import argparse
import textwrap
import sys

from pathlib import Path

import zipfile

import re
import html

import seaborn as sns
import pandas as pd

VERSION = 1.0


def init():
    arg_parser = argparse.ArgumentParser(description="print html table made of csv with estimation",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:
  

  For '--part_color', is you want to use comma(,) an colon(:) in word, then those must be escaped by "\".


example:
  cat test3.csv
IDX,B,C,O,I,A
1,A,Sample1,Observation1:this is a pen,Investigation1:Atre you there?,Action1: nothing to do
2,B,Sample2,Observation2:this is a pen,Investigation2:Atre you there?,Action2: nothing to do
3,C,Sample3,Observation3:this is a pen,Investigation2:Atre you there?,Action3: nothing to do

  csv_print_html_oia.py --columns=IDX,B,C --part_color='this:red' test3.csv  O I A > test.html
  csv_print_html_oia.py --columns=IDX,B,C --part_color='バリ島:red,米国:green,潜水艦:blue,海軍:black' --search_on_html test3.csv  O I A > test.html

'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))

    arg_parser.add_argument("--title", dest="TITLE", help="Title of table", type=str, metavar='TITLE', default=None)

    arg_parser.add_argument("--columns",
                            dest="COLUMNS",
                            help="names of addtional columns",
                            type=str,
                            metavar='COLUMNS[,COLUMNS...]',
                            default=None)

    arg_parser.add_argument("--part_color",
                            dest="PCOLORS",
                            help="part color for string, color code is one in css codes.",
                            type=str,
                            metavar='STRING:COLOR[,STRING:COLOR...]',
                            default=None)
    arg_parser.add_argument("--search_on_html", dest="SHTML", help="searching on html is enable", action="store_true", default=False)

    arg_parser.add_argument("--output_file", dest="OUTPUT", help="path of output file", type=str, metavar='FILE', default=sys.stdout)

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='file to read, if empty, stdin is used')

    arg_parser.add_argument('oia_columns', metavar='COLUMNS', nargs="+", help="colum names of Observation/Investigation/Action")

    args = arg_parser.parse_args()
    return args


def html_prologe_oia(align_center=True, width=None, word_colors="", search_on_html=False, title=""):
    table_css_2 = ""
    if align_center:
        table_css_2 += "margin-left: auto;margin-right: auto;"
    if width is not None:
        table_css_2 += "width:{};".format(width)
    table_css = '''
    <style type="text/css">
      /* */
      body {{
        background: -webkit-linear-gradient(left, #25c481, #25b7c4);
        background: linear-gradient(to right, #25c481, #25b7c4);
      }}
      h2.title {{
        text-align:center;
        margin-bottom: 0pt;
      }}
      span.word_view_span {{
        font-weight:bold;
        background:#EEEEEE;
        box-shadow: 1px 1px 1px 1px rgba(0,0,0,0.4);
        border-radius: 4px;
        padding-left:0.5em;
        padding-right:0.5em;
	margin-right:2pt;
      }}
      fieldset {{
        border:  1px solid #ccc;
        border-radius: 5px;
        padding: 25px;
        margin-top: 20px;
      }}
      legend {{
        border:  1px solid #ccc;
        border-bottom: 0;
        border-radius: 5px 5px 0 0;
        padding: 8px 18px 0;
        position:relative;
        top: -14px;
      }}

      table {{ 
         {}
         box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
      }}
      table caption {{
         font-size:large; font-weight: bold;
      }}
      th {{
          /* background-color: #6495ed; */
         background-color: #009879;
	 padding:6px;
      }}
      thead tr th {{
         border-bottom: solid 1px;
         color: #ffffff;
      }}
      td {{
         padding:6pt; 
      }}
      /* Table CSS: Creating beautiful HTML tables with CSS - DEV Community https://dev.to/dcodeyt/creating-beautiful-html-tables-with-css-428l */
      tbody tr {{
         border-bottom: 1px solid #dddddd;
         background-color: #ffffff;
      }}
      tbody tr:last-of-type {{
         border-bottom: 2px solid #009879;
      }}
      /*  CSSのposition: stickyでテーブルのヘッダー行・列を固定する - Qiita https://qiita.com/orangain/items/6268b6528ab33b27f8f2 */
      table.sticky_table thead th {{
         position: -webkit-sticky;
         position: sticky;
         top: 0;
         z-index: 1;
      }}
      table.sticky_table th:first-child {{
         position: -webkit-sticky;
         position: sticky;
         left: 0;
      }}
      table.sticky_table thead th:first-child {{
         z-index: 2;
      }}

    </style>
'''.format(table_css_2)

    text = """
<?xml version="1.0" encoding="utf-8"?>
<html>
  <!- made by csv_print_html_oia.py -->
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Cache-Control" content="no-store">
    <meta http-equiv="Expires" content="0">
{}
  </head>
  <body>
""".format(table_css)
    if title is not None and len(title) > 0:
        text += f'<h2 class="title">{title}</h2>'

    if search_on_html:
        text += """
   <script type="text/javascript">
        function word_color(word,color_code){{
            var nodes= document.getElementsByTagName("td");
            for(var i=0; i< nodes.length; i++){{
                let wre= word.replace(/[\\^$.*+?()[\]{{}}|]/g, '\\$&');
                wre= wre.replace(/</g, '&lt;');
                wre= wre.replace(/>/g, '&gt;');
                let re= new RegExp('('+wre+')','gi');
                nodes[i].innerHTML=nodes[i].innerHTML.replace(re,'<span class="word_view_span" style="color:'+color_code+'">$1</span>');
            }}
        }}
        function word_color_reset(){{
            var nodes= document.getElementsByTagName("td");
            for(var i=0; i< nodes.length; i++){{
                let re = new RegExp('<span class="word_view_span" style="color:[^\"]+">([^<]+?)</span>','gi');
                nodes[i].innerHTML=nodes[i].innerHTML.replace(re,'$1');
            }}
        }}

        function emphasis_words(obj){{
            var wc_defs= obj.value;
            let re= /\s*(?<!\\\\),\s*/;
            var cvs= wc_defs.split(re);
            word_color_reset();
            cvs.forEach(
                function (val ){{
                    let re= /\s*(?<!\\\\):\s*/;
                    cvs=val.split(re);
                    if( cvs.length < 2){{
                        alert("??error:word_view:invalid definition:"+wc_defs);
                    }} else {{
                        var w= cvs[0];
                        var c= cvs[1];
                        word_color(w,c);
                    }}
                }}
            );
        }}
   </script>
    <form action="" onsubmit="return false;">
      <fieldset style="padding-top:0pt;padding-bottom:0pt;">
	<legend>極色付け定義</legend>
	<input type="text" size="80" placeholder="Enter word:color[,word:color...]" onchange="emphasis_words(this)" value="{}"></input><br/>
        <span style="font-size:small;">
	語句の色付け定義を"語句:色"で入力。複数入力する場合は半角カンマで区切って入力、語句に半角カンマ、コロンを含める場合はBackslash(\\)によりエスケープする必要がある。<br>
        Ex: ABC:red,DEF\,GHI:blue,\d+人:black
        </span>
      </fieldset>
    </form>
""".format(word_colors)

    return text


def html_epiloge(datatable=False):
    # DataTables example - Scroll - horizontal and vertical https://datatables.net/examples/basic_init/scroll_xy.html
    if datatable:
        text = '''
<script type="text/javascript">$(document).ready(function(){$('table').DataTable({
    lengthChange: false,
    scrollX: true,
    scrollY: "80vh",
    paging: false
});});</script>
'''
    else:
        text = ""

    text += '''
  </body>
</html>
'''
    return text


def part_color(pcolors, text):
    for pc in pcolors:
        cvs = re.split(r"(?<!\\):", pc)
        if len(cvs) < 2:
            print(f"??error:csv_print_html:invalid format for --part_color:{pc}", file=sys.stderr)
            sys.exit(1)
        w = cvs[0]
        w = re.sub(r"\\([,:])", r"\1", w)
        w = w.strip("'\"")
        w = html.escape(w)
        w0 = "(" + w + ")"
        c = cvs[1]
        fmt = f"color:{c};"
        sp = f'<span class="word_view_span" style="{fmt}">\\1</span>'
        text = re.sub(w0, sp, text)
    return text


def make_table(df, columns, oia_columns, pcolors, space_width="40pm"):
    html_str = '\n<table class="sticky_table display nowrap" style="width:100%;">\n'
    html_str += '<thead>\n'
    n_oia = len(oia_columns)
    for c in columns:
        html_str += f"<th>{c}</th>\n"
    html_str += f'<th colspan="{n_oia+1}">Observation/Investigation/Action</th>\n'
    html_str += '</thead>\n<tbody>\n'

    for ir, row in df.iterrows():
        if ir % 2 == 0:
            tr_sty = 'style="background-color:#eeffee;"'
        else:
            tr_sty = ""
        html_str += f"<tr {tr_sty}>\n"
        for c in columns:
            v = html.escape(str(row[c]))
            if pcolors is not None and len(pcolors) > 0:
                v = part_color(pcolors, v)
            html_str += f'<td rowspan="{n_oia}">{v}</td>\n'
        for ic, c in enumerate(oia_columns):
            v = html.escape(str(row[c]))
            if pcolors is not None and len(pcolors) > 0:
                v = part_color(pcolors, v)
            html_str += (f'<td width="{space_width}"></td>' * ic) + f'<td colspan="{4-ic}">{v}</td>\n'
            if ic < len(oia_columns) - 1:
                html_str += f'</tr>\n<tr {tr_sty}>\n'
        html_str += "</tr>\n"
    html_str += "</tbody>\n</table>\n"

    return html_str


if __name__ == "__main__":
    args = init()
    csv_file = args.csv_file
    output_file = args.OUTPUT
    oia_columns = args.oia_columns

    title = args.TITLE
    columns_s = args.COLUMNS

    pcolors_s = args.PCOLORS

    search_on_html = args.SHTML

    pcolors = None
    if pcolors_s is not None:
        pcolors = re.split(r"\s*(?<!\\),\s*", pcolors_s)
        print(f"%inf:csv_print_html:part colors: {pcolors}", file=sys.stderr)

    columns = []
    if columns_s is not None:
        columns = re.split(r"\s*,\s*", columns_s)

    if csv_file == "-":
        csv_file = sys.stdin

    if output_file != sys.stdout:
        output_file = open(output_file, "w")

    csv_df = pd.read_csv(csv_file)

    html_str = html_prologe_oia(width=None, word_colors=pcolors_s, search_on_html=search_on_html, title=title)
    html_str += "<div id='tablecontainer'>"
    table_str = make_table(csv_df, columns, oia_columns, pcolors)
    html_str += table_str
    html_str += "</div>"
    html_str += html_epiloge()

    print(html_str, file=output_file)
