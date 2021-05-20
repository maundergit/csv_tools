#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_print_html.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-11-08 11:46:33>
# Licence:
#  Copyright (c) 2021 Masaharu N. Akei
#
#  This software is released under the MIT License.
#    http://opensource.org/licenses/mit-license.php
# ----------------------------------------------------------------------
import argparse
import textwrap
import sys

from pathlib import Path

import zipfile

import re
import html
from lxml import etree
from io import StringIO

import minify_html

import seaborn as sns
import pandas as pd

VERSION = 1.0


def init():
    arg_parser = argparse.ArgumentParser(description="print html table made of csv with estimation",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:
  Elements in only columns, that has int64/float64 as dtype, will be processed.
  So in the following, "8" in Row=4,Col=D is not evaluated for 'max'/'min' and so on.
    | A | B | C | D |
    | - | - | - | - |
    | 1 | 0 | 1 | a |
    | 2 | 2 | 0 | b |
    | 3 |   | 3 |   |
    |   |   | 4 | d |
    | 4 | 6 | 7 | 8 |

  When '--bar' is used, others than '--trim_null' are not available.

  For '--part_color', is you want to use comma(,) an colon(:) in word, then those must be escaped by "\".

  NOTE:NOW, '--max_column_width' is not available.

example:
  csv_print_html.py --highlight=2 --gradient=all --max_in_col=all --min_in_col=all t1.csv > test.html
  csv_print_html.py --bar=all --trim_null="-"=all t1.csv > test.html
  csv_print_html.py --min_in_col=0:1 t1.csv > test.html
  csv_print_html.py --min_in_col=,A:B t1.csv > test.html
  csv_print_html.py --highlight=2 --title=HightLight=2 t1.csv > test.html
  csv_print_html.py --bar=all --trim_null="-"=all --columns=A,B,C t1.csv > test.html
  csv_print_html.py --min_in_row=all t1.csv > test.html
  csv_print_html.py --part_color="Joseph:red,Beesley\, Mr. Lawrence:blue" titanic.csv > test.html
  csv_print_html.py --part_color='Joseph:red,Beesley\, Mr. Lawrence:blue,female:green,C\d+:black' titanic.csv > test.html
  csv_print_html.py --part_color='Joseph:red,Beesley\, Mr. Lawrence:blue,female:green,C\d+:black' --column_width="Name:128px" titanic.csv > test.html

'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))

    arg_parser.add_argument("--title", dest="TITLE", help="Title of table", type=str, metavar='TITLE', default=None)

    arg_parser.add_argument("--columns",
                            dest="COLUMNS",
                            help="names of columns to do",
                            type=str,
                            metavar='COLUMNS[,COLUMNS...]',
                            default=None)

    arg_parser.add_argument("--fp_precision", dest="FP_PREC", help="precision of float, default=2", type=int, metavar='INT', default=2)

    arg_parser.add_argument("--trim_null",
                            dest="TNULL",
                            help="triming null value",
                            type=str,
                            metavar='STRING=(all or ROW:ROW,COL:COL)',
                            default=None)
    arg_parser.add_argument("--highlight",
                            dest="HLIGHT",
                            help="highlighting more than threshold",
                            type=str,
                            metavar='FLOAT[=(all or ROW:ROW,COL:COL)]',
                            default=None)
    arg_parser.add_argument("--min_in_column",
                            dest="HMINCOL",
                            help="highlighting minimum cell in each column",
                            type=str,
                            metavar='(all or ROW:ROW,COL:COL)',
                            default=None)
    arg_parser.add_argument("--max_in_column",
                            dest="HMAXCOL",
                            help="highlighting maximum cell in each column",
                            type=str,
                            metavar='(all or ROW:ROW,COL:COL)',
                            default=None)
    arg_parser.add_argument("--min_in_row",
                            dest="HMINROW",
                            help="highlighting minimum cell in each row",
                            type=str,
                            metavar='(all or ROW:ROW,COL:COL)',
                            default=None)
    arg_parser.add_argument("--max_in_row",
                            dest="HMAXROW",
                            help="highlighting maximum cell in each row",
                            type=str,
                            metavar='(all or ROW:ROW,COL:COL)',
                            default=None)
    arg_parser.add_argument("--gradient",
                            dest="GRADIENT",
                            help="gradient mode",
                            type=str,
                            metavar='(all or ROW:ROW,COL:COL)',
                            default=None)
    arg_parser.add_argument("--bar",
                            dest="BAR",
                            help="histogram of each column",
                            type=str,
                            metavar='(all or ROW:ROW,COL:COL)',
                            default=None)

    arg_parser.add_argument("--max_column_width",
                            dest="MAX_CWIDTH",
                            help="maximum width of all columns, default='200pm'",
                            type=str,
                            metavar="WIDTH",
                            default="200pm")
    arg_parser.add_argument("--column_width",
                            dest="CWIDTHS",
                            help="widths of columns",
                            type=str,
                            metavar="COLUMN:WIDTH[,COLUMN:WIDTH..]",
                            default=None)
    arg_parser.add_argument("--part_color",
                            dest="PCOLORS",
                            help="part color for string, color code is one in css codes.",
                            type=str,
                            metavar='STRING:COLOR[,STRING:COLOR...]',
                            default=None)
    arg_parser.add_argument("--search_on_html", dest="SHTML", help="searching on html is enable", action="store_true", default=False)

    arg_parser.add_argument("--datatable", dest="DATATBL", help="datatble mode", action="store_true", default=False)
    arg_parser.add_argument("--output_file", dest="OUTPUT", help="path of output file", type=str, metavar='FILE', default=sys.stdout)
    arg_parser.add_argument("--minify", dest="MINIFY", help="minifing html", action="store_true", default=False)

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='files to read, if empty, stdin is used')

    args = arg_parser.parse_args()
    return args


def set_caption(dsty, title):
    res = dsty.set_caption(title)
    return res


def set_fp_precision(dsty, fp_precision):
    res = dsty.set_precision(fp_precision)
    return res


def plot_bar(dsty, df_slice=None, axis=0, width=100, align="mid", vmin=None, vmax=None):

    res = dsty.bar(subset=df_slice, axis=axis, align=align, color=['#d65f5f', '#5fba7d'], width=width, vmin=vmin, vmax=vmax)
    return res


def set_css(dsty, css_dict, df_slice=None):
    res = dsty.set_properties(**css_dict, subset=df_slice)
    return res


def trim_null(dsty, text, bg_color="#808080;text-align:center;", df_slice=None):
    if df_slice is None:
        res = dsty.set_na_rep(text).highlight_null(bg_color)
    else:
        res = dsty.highlight_null(bg_color, sbuset=df_slice).format(None, na_rep=text, subset=df_slice)
    return res


def highlight_max(dsty, bg_color="yellow", axis=0, df_slice=None):
    """FIXME! briefly describe function

    :param dsty: 
    :param bg_color: 
    :param axis: 0=index,1=column, None=all elements
    :returns: 
    :rtype: 

    """
    res = dsty.highlight_max(color=bg_color, axis=axis, subset=df_slice)
    return res


def highlight_min(dsty, bg_color="#ffd700", axis=0, df_slice=None):
    """FIXME! briefly describe function

    :param dsty: 
    :param bg_color: 
    :param axis: 0=index,1=column, None=all elements
    :returns: 
    :rtype: 

    """
    res = dsty.highlight_min(color=bg_color, axis=axis, subset=df_slice)
    return res


def _threshold_highlight(x):
    #print(x, type(x), isinstance(x, float), file=sys.stderr)
    if isinstance(x, (float, int)) and x < 2.0:
        print("IN=", x, file=sys.stderr)
        return "color:red"
    else:
        return "color:black"


#def threshold_highlight(dsty, v_thre, css_low="color:red", css_high="color:black", df_slice=None):
def threshold_highlight(dsty, v_thre, css_low="color:red", css_high="", df_slice=None):

    res = dsty.applymap(lambda x: css_low if isinstance(x, (float, int)) and x < v_thre else css_high, subset=df_slice)
    #res = dsty.applymap(_threshold_highlight, subset=df_slice)
    return res


def gradient_style(dsty, axis=None, cmap="green", vmin=None, vmax=None, df_slice=None):
    """FIXME! briefly describe function

    :param dsty: 
    :param axis: 0=index,1=column, None=all elements
    :param cmap: 
    :returns: 
    :rtype: 

    """
    cm = sns.light_palette(cmap, as_cmap=True)

    bg_params = {"subset": df_slice}
    if vmin is not None:
        bg_params.update({"vmin": vmin})
    if vmax is not None:
        bg_params.update({"vmax": vmax})

    res = dsty.background_gradient(axis=axis, cmap=cm, **bg_params)
    return res


def make_df_slicer(rc_range_s):
    cvs = re.split(r"\s*(?<!\\),\s*", rc_range_s)

    if len(cvs[0]) > 0:
        nrs = re.split(r"\s*(?<!\\):\s*", cvs[0])
    else:
        nrs = None
    ncs = None
    if len(cvs) > 1:
        if len(cvs[1]) > 0:
            ncs = re.split(r"\s*(?<!\\):\s*", cvs[1])

    res = pd.IndexSlice
    if nrs is None:
        res = res[:, ncs[0]:ncs[1]]
    elif ncs is None:
        res = res[nrs[0]:nrs[1], :]
    else:
        res = res[nrs[0]:nrs[1], ncs[0]:ncs[1]]
    return res


def do_highlight(dsty, ht_defs):
    cvs = re.split(r"\s*(?<!\\)=\s*", ht_defs)
    thres = float(cvs[0])
    sset = None
    if len(cvs) > 1:
        if cvs[1] == "all":
            sset = None
        else:
            sset = make_df_slicer(cvs[1])

    dsty = threshold_highlight(dsty, thres, df_slice=sset)
    return dsty


def do_highlight_max(dsty, hmax_defs, axis=0):
    if hmax_defs == "all":
        sset = None
    else:
        sset = make_df_slicer(hmax_defs)

    dsty = highlight_max(dsty, bg_color="yellow", axis=axis, df_slice=sset)
    return dsty


def do_highlight_min(dsty, hmin_defs, axis=0):
    if hmin_defs == "all":
        sset = None
    else:
        sset = make_df_slicer(hmin_defs)

    dsty = highlight_min(dsty, bg_color="#ffd700", axis=axis, df_slice=sset)
    return dsty


def do_bar_plot(dsty, bar_defs):
    if bar_defs == "all":
        sset = None
    else:
        sset = make_df_slicer(bar_defs)

    dsty = plot_bar(dsty, df_slice=sset, axis=0, width=100, align="mid", vmin=None, vmax=None)
    return dsty


def do_trim_null(dsty, tnull_defs):
    cvs = re.split(r"\s*(?<!\\)=\s*", tnull_defs)
    text = cvs[0]
    sset = None
    if len(cvs) > 1:
        if cvs[1] == "all":
            sset = None
        else:
            sset = make_df_slicer(cvs[1])

    dsty = trim_null(dsty, text, df_slice=sset)
    return dsty


def html_prologe(align_center=True, width=None, datatable=False, word_colors="", search_on_html=False):
    table_css = ""
    datatable_header = ""
    if datatable:
        datatable_header = '''
<!--
    <script type="text/javascript" src="https://code.jquery.com/jquery-3.5.1.js"></script>
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.23/css/jquery.dataTables.css">
    <script type="text/javascript" src="https://cdn.datatables.net/1.10.23/js/jquery.dataTables.js"></script>
-->
    <script type="text/javascript" src="csv_print_html/jquery-3.5.1.min.js"></script>
    <link rel="stylesheet" type="text/css" href="csv_print_html/datatables.min.css"/>
    <script type="text/javascript" src="csv_print_html/datatables.min.js"></script>
  <style type="text/css">
    div.dataTables_wrapper {
        width: 100%;
        margin: 0 auto;
    }
  </style>
'''
    else:
        if align_center:
            table_css += "margin-left: auto;margin-right: auto;"
        if width is not None:
            table_css += "width:{};".format(width)
        # text-shadow: 0.1em 0.1em 0.6em gold;
        table_css = '''
    <style type="text/css">
      /* */
      body {{
        background: -webkit-linear-gradient(left, #25c481, #25b7c4);
        background: linear-gradient(to right, #25c481, #25b7c4);
      }}
      form.word_search {{
        position: fixed;
        top: 1em;
        visibility:hidden;
        z-index: 100;
      }}
      span.word_view_span {{
        font-weight:bold;
        background:#EEEEEE;
        box-shadow: 0.0625em 0.0625em 0.0625em 0.0625em rgba(0,0,0,0.4);
        border-radius: 0.25em;
        padding-left:0.2em;
        padding-right:0.2em;
	margin-right:0.2em;
      }}
      fieldset {{
        border: 2px solid #ccc;
        border-radius: 5px;
        padding: 25px;
        margin-top: 20px;
        background-color: #e0ffff;
        box-shadow: 5px 5px 5px rgba(0,0,0,0.2);
      }}
      legend {{
        border:  1px solid #ccc;
        border-bottom: 0;
        border-radius: 5px 5px 0 0;
        padding: 8px 18px 0;
        position:relative;
        top: -14px;
        background-color: #e0ffff;
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
      /* Table CSS: Creating beautiful HTML tables with CSS - DEV Community https://dev.to/dcodeyt/creating-beautiful-html-tables-with-css-428l */
      tbody tr {{
         border-bottom: 1px solid #dddddd;
         background-color: #ffffff;
      }}
      tbody tr:nth-of-type(even) {{
         background-color: #f3f3f3;
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
'''.format(table_css)

    text = """
<?xml version="1.0" encoding="utf-8"?>
<html>
  <!-- made by csv_print_html.py -->
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Cache-Control" content="no-store">
    <meta http-equiv="Expires" content="0">
{}
{}
  </head>
  <body>
""".format(table_css, datatable_header)

    word_colors = re.sub(r"\"", "&quot;", word_colors)
    if search_on_html:
        text += """
   <script type="text/javascript">
        window.onload=function(){{
            if( window.location.hash.length > 0){{
                window.scroll(0,window.scrollY-32);
            }}
            if( window.location.search.length > 0){{
                let search_string=decodeURI(window.location.search.substring(1));
                window.find(search_string,false,false,true,false,true);
            }}
        }}
        function show_nrec_record(nrec,onoff){{
            let tr_objs= document.evaluate("/html//tr[@nrec=\\""+nrec+"\\"]",document,null,XPathResult.ANY_TYPE, null);
            let tr_node= tr_objs.iterateNext();
            while(tr_node){{
                if( onoff ){{
                    tr_node.style.display="";
                }} else {{
                    tr_node.style.display="none";
                }}
                tr_node= tr_objs.iterateNext();
            }}
        }}
        function show_nohits_record(obj){{
            if( obj.checked){{
                onoff=true;
            }} else {{
                onoff=false;
            }}
            let xp_results_0= document.evaluate("/html//td[@hits_status=\\"1\\"]",document,null,XPathResult.ANY_TYPE, null);
            let node= xp_results_0.iterateNext();
            let nrec_hits=[];
            while( node){{
                let nrec= node.getAttribute("nrec");
                nrec_hits.push(nrec);
                show_nrec_record(nrec,true);
                node= xp_results_0.iterateNext();
            }}
            show_nrec_record(onoff);
            let xp_results= document.evaluate("/html//td[@hits_status=\\"0\\"]",document,null,XPathResult.ANY_TYPE, null);
            node= xp_results.iterateNext();
            while( node){{
                let nrec= node.getAttribute("nrec");
                if( nrec_hits.indexOf(nrec) != -1){{
                    node= xp_results.iterateNext();
                    continue;
                }}
                show_nrec_record(nrec, onoff);
                node= xp_results.iterateNext();
            }}
        }}
        function word_color(word,color_code){{
            var nodes= document.getElementsByTagName("td");
            let count=0;
            for(var i=0; i< nodes.length; i++){{
                // let wre= word.replace(/[\\^$.*+?()\\[\\]{{}}|]/g, '\\\\$&');
                let wre= word.replace(/</g, '&lt;');
                wre= wre.replace(/>/g, '&gt;');
                let re= new RegExp('(?<!<[^>]*)('+wre+')','gi');
                nodes[i].innerHTML=nodes[i].innerHTML.replace(re,'<span class="word_view_span" style="color:'+color_code+'">$1</span>');
                count_0= (nodes[i].innerHTML.match(re) ||[]).length;
                if( count_0 > 0){{
                    nodes[i].setAttribute("hits_status","1");
                }} else {{
                    nodes[i].setAttribute("hits_status","0");
                }}
                count= count+ count_0;
            }}
            return count;
        }}
        function word_color_reset(){{
            var nodes= document.getElementsByTagName("td");
            for(var i=0; i< nodes.length; i++){{
                span_head='<span class="word_view_span"'
                let re = new RegExp(span_head+' style="color:[^\"]+">([^<]+?)</span>','gi');
                while( nodes[i].innerHTML.indexOf(span_head) != -1){{
                    nodes[i].innerHTML=nodes[i].innerHTML.replace(re,'$1');
                    nodes[i].setAttribute("hits_status","0");
                }}
            }}
        }}
        function emphasis_words(obj){{
            let wc_defs= obj.value;
            let re_s= new RegExp(/(?<!\\\\)\s*,\s*/,'g')
            obj.value= obj.value.replace(re_s,", ");
            let re= /\s*(?<!\\\\),\s*/;
            let cvs= wc_defs.split(re);
            let word_counts={{}};
            word_color_reset();
            cvs.forEach(
                function (val ){{
                    if(val==""){{
                        return;
                    }}
                    let re= /\s*(?<!\\\\):\s*/;
                    cvs=val.split(re);
                    var w="";
                    var c="";
                    if( cvs.length < 2){{
                        // alert("??error:word_view:invalid definition: '"+val+"'");
                        w= cvs[0];
                        c="red";
                    }} else {{
                        let re= new RegExp('\\\\\\\\([,:])','g');
                        w= cvs[0];
                        w=w.replace(re,'$1');
                        c= cvs[1];
                    }}
                    if(!c.match(/^[a-zA-Z0-9#]+$/)){{
                        alert("??error:word_view:invalid color code: '"+c+"'");
                        return;
                    }}
                    try{{
                        word_counts[String(w)]=word_color(w,c);
                    }} catch(e){{
                        alert("??error:word_view:invalid definition: '"+val+"' :"+e);
                    }}
                }}
            );
            let sh_obj= document.getElementById("showhide_hits");
            show_nohits_record(sh_obj);
            let swr= document.getElementById('search_word_result');
            swr.innerHTML="検索結果:"+JSON.stringify(word_counts);
        }}
        function show_word_search(){{
            let fobj= document.getElementById("word_search");

            sty_visibility=fobj.style.visibility;
            if( sty_visibility == "" || sty_visibility == "hidden"){{
                fobj.style.visibility="visible"
            }} else {{
                fobj.style.visibility="hidden"
            }}
        }}
   </script>
    <form action="" onsubmit="return false;" class="word_search" id="word_search" ondblclick="show_word_search();">
      <fieldset style="padding-top:0pt;padding-bottom:0pt;">
	<legend>語句色付け定義</legend>
	<input type="text" size="138" placeholder="Enter word:color[,word:color...]" onchange="emphasis_words(this)" value="{}"><br/>
	<input type="checkbox" id="showhide_hits" name="showhide_hits" checked onchange="show_nohits_record(this)"/>
        <label for="showhide_hist" style="font-size:0.5em;">全レコード表示</label><br/>
        <span style="font-size:0.5em;">
	語句の色付け定義を"語句:色"で入力。複数入力する場合は半角カンマで区切って入力、語句には正規表現を利用可能<br>
        語句だけ指定した場合は、赤色が指定されたものとして処理される。
        語句に半角カンマ、コロンを含める場合はBackslash(\\)によりエスケープする必要がある。
        また、&lt;&gt;は検索時に&amp;lt;&amp;gt;として検索されることに注意。<br>
        Ex: ABC:red,DEF\,GHI:blue,\d+人:black
        </span><br>
        <span style="font-size:small;" id="search_word_result"></span>
      </fieldset>
    </form>
""".format(word_colors)
    else:
        text += f'<input value="{word_colors}" style="display:none" />\n'

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
    hit_words = {}
    for pc in pcolors:
        cvs = re.split(r"(?<!\\):", pc)
        if len(cvs) < 2:
            # print(f"??error:csv_print_html:invalid format for --part_color:{pc}", file=sys.stderr)
            # sys.exit(1)
            cvs.append("red")
        w = cvs[0]
        w = re.sub(r"\\([,:])", r"\1", w)
        w = w.strip("'\"")
        w_0 = w
        w = html.escape(str(w))
        w0 = "(" + w + ")"
        c = cvs[1]
        # fmt = f"color:{c};font-weight:bold;background:#EEEEEE;box-shadow: 1px 1px 1px 1px rgba(0,0,0,0.4);border-radius: 4px;padding-left:0.5em;padding-right:0.5em;"
        fmt = f"color:{c};"
        sp = f'<span class="word_view_span" style="{fmt}">\\1</span>'
        text_0 = text
        text = re.sub(w0, sp, text)
        if text_0 != text:
            hit_words[w_0] = text_0.count(w_0)
    return text, hit_words


def set_max_column_width(df_sty, max_width="200px"):
    df_sty.set_properties(subset=list(df_sty.columns), **{'max-width': max_width})
    return df_sty


def set_column_width(column_widths, df_sty):
    print(f"%inf;csv_print_html:column widths:{column_widths}", file=sys.stderr)
    for cw in column_widths:
        cvs = re.split(r"(?<!\\):", cw)
        if len(cvs) < 2:
            print(f"??error:csv_print_html:invalid format for --column_width:{cw}", file=sys.stderr)
            sys.exit(1)
        c = cvs[0]
        w = cvs[1]
        if c not in df_sty.columns:
            print(f"??error:csv_print_html:column {c} was not found for {cw}", file=sys.stderr)
            sys.exit(1)
        df_sty.set_properties(subset=[c], **{'width': w})
    return df_sty


def set_rid_in_html(html_str):
    html_parser = etree.HTMLParser()
    tree = etree.parse(StringIO(html_str), html_parser)
    html_root = tree.getroot()
    idx = 0
    for elm in html_root.xpath(f'//*/table[@class="sticky_table display nowrap"]/tbody/tr'):
        elm.set("id", f"rid_{idx}")
        elm.set("nrec", f"{idx}")
        for elm_c in elm.xpath("./td"):
            elm_c.set("nrec", f"{idx}")
            elm_c.set("hits_status", "0")
        idx += 1
    for elm in html_root.xpath(f'//*/span[@class="word_view_span"]/ancestor::td'):
        elm.set("hits_status", "1")
    html_str_r = etree.tostring(html_root, encoding="utf8", method="html")
    html_str_r = html_str_r.decode('utf8')
    return html_str_r


if __name__ == "__main__":
    args = init()
    csv_file = args.csv_file
    output_file = args.OUTPUT
    datatable_mode = args.DATATBL

    title = args.TITLE
    columns_s = args.COLUMNS

    fp_prec = args.FP_PREC
    bg_gradient = args.GRADIENT
    highlight = args.HLIGHT
    h_max_col = args.HMAXCOL
    h_min_col = args.HMINCOL
    h_max_row = args.HMAXROW
    h_min_row = args.HMINROW
    bar_mode = args.BAR
    tnull = args.TNULL

    max_column_width = args.MAX_CWIDTH
    column_widths_s = args.CWIDTHS
    pcolors_s = args.PCOLORS
    search_on_html = args.SHTML

    html_minify = args.MINIFY

    pcolors = None
    if pcolors_s is not None:
        pcolors = re.split(r"\s*(?<!\\),\s*", pcolors_s)
        print(f"%inf:csv_print_html:part colors: {pcolors}", file=sys.stderr)
    else:
        pcolors_s = ""

    column_widths = None
    if column_widths_s is not None:
        column_widths = re.split(r"\s*(?<!\\),\s*", column_widths_s)

    if datatable_mode:
        misc_zip_name = "csv_print_html_misc.zip"
        scr_path = Path(__file__).resolve()
        scr_dir = scr_path.parent
        misc_zip_path = scr_dir / misc_zip_name
        if misc_zip_path.exists():
            with zipfile.ZipFile(misc_zip_path, "r") as zip_f:
                zip_f.extractall("csv_print_html")
            print("%inf:csv_print_html:jquery and datatable kit was extracted to current directory", file=sys.stderr)
        else:
            datatable_mode = False
            print("#warn:csv_print_html: {} was not found".format(misc_zip_name), file=sys.stderr)
    if datatable_mode:
        if search_on_html:
            print("#warn:csv_print_html:search_on_html is disable for datatable_mode", file=sys.stderr)
        search_on_html = False

    if bar_mode is not None and (h_max_col is not None or h_min_col is not None or h_max_row is not None or h_min_row is not None
                                 or highlight is not None or bg_gradient is not None):
        print("??error:csv_print_html:invalid combination of options:'--bar' must be used without others.", file=sys.stderr)
        sys.exit(1)
    if (h_min_col is not None or h_max_col is not None) and (h_min_row is not None or h_max_row is not None):
        print("??error:csv_print_html:invalid combination of options:'--min_in_col'/'--max_in_col' and '--min_in_row'/'--max_in_row'",
              file=sys.stderr)
        sys.exit(1)

    columns = []
    if columns_s is not None:
        columns = re.split(r"\s*,\s*", columns_s)

    if csv_file == "-":
        csv_file = sys.stdin

    if output_file != sys.stdout:
        output_file = open(output_file, "w")

    # Styling  pandas 1.1.4 documentation https://pandas.pydata.org/docs/user_guide/style.html
    csv_df = pd.read_csv(csv_file, dtype='object')

    if len(columns) > 0:
        csv_df = csv_df[columns]

    csv_df.fillna("", inplace=True)
    csv_df = csv_df.applymap(lambda x: html.escape(str(x)))

    if pcolors is not None and len(pcolors) > 0:
        csv_df = csv_df.applymap(lambda x: part_color(pcolors, str(x))[0])
    # print(csv_df.describe())

    # csv_df.reset_index(inplace=True)
    df_sty = csv_df.style

    df_sty = set_fp_precision(df_sty, fp_prec)
    # df_sty = df_sty.set_properties(**{'border-color': '#c0c0c0'})

    # background gradient
    if bg_gradient is not None:
        if bg_gradient == "all":
            df_sty = gradient_style(df_sty, df_slice=None)
        else:
            df_slice = make_df_slicer(bg_gradient)
            df_sty = gradient_style(df_sty, df_slice=df_slice)

    # highlight
    if highlight is not None:
        df_sty = do_highlight(df_sty, highlight)

    # highlight maximum in col
    if h_max_col is not None:
        df_sty = do_highlight_max(df_sty, h_max_col)
    # highlight minimum in col
    if h_min_col is not None:
        df_sty = do_highlight_min(df_sty, h_min_col)

    # highlight maximum in row
    if h_max_row is not None:
        df_sty = do_highlight_max(df_sty, h_max_row, axis=1)
    # highlight minimum in row
    if h_min_row is not None:
        df_sty = do_highlight_min(df_sty, h_min_row, axis=1)

    if tnull:
        df_sty = do_trim_null(df_sty, tnull)

    # bar mode
    if bar_mode is not None:
        df_sty = do_bar_plot(df_sty, bar_mode)

    if title is not None:
        df_sty = set_caption(df_sty, title)

    df_sty = set_max_column_width(df_sty, max_width=max_column_width)
    # df_sty.set_table_attributes('class="sticky_table display nowrap" style="width:100%"')
    df_sty.set_table_attributes('class="sticky_table display nowrap"')
    if column_widths is not None:
        df_sty = set_column_width(column_widths, df_sty)

    html_str = html_prologe(width=None, datatable=datatable_mode, word_colors=pcolors_s, search_on_html=search_on_html)
    html_str += "<div id='tablecontainer'>"
    table_str = df_sty.render()

    # table_str = re.sub(r"<table ([^>]+)>", r"<table \1 class='display nowrap' style='width:100%'>", table_str)
    html_str += table_str
    html_str += "</div>"
    html_str += html_epiloge(datatable=datatable_mode)

    html_str = re.sub(r"<thead", '<thead ondblclick="show_word_search();"', html_str)
    html_str = set_rid_in_html(html_str)

    if html_minify:
        try:
            html_str = minify_html.minify(html_str, minify_js=True, minify_css=True)
        except SyntaxError as e:
            mes = f'??error:csv_print_html_oia:{e}'
            print(mes, file=sys.stderr)
            sys.exit(1)

    print(html_str, file=output_file)
