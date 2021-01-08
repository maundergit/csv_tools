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

example:
  csv_print_html.py --highlight=2 --gradient=all --max_in_col=all --min_in_col=all t1.csv > test.html
  csv_print_html.py --bar=all --trim_null="-"=all t1.csv > test.html
  csv_print_html.py --min_in_col=0:1 t1.csv > test.html
  csv_print_html.py --min_in_col=,A:B t1.csv > test.html
  csv_print_html.py --highlight=2 --title=HightLight=2 t1.csv > test.html
  csv_print_html.py --bar=all --trim_null="-"=all --columns=A,B,C t1.csv > test.html
  csv_print_html.py --min_in_row=all t1.csv > test.html

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

    arg_parser.add_argument("--datatable", dest="DATATBL", help="datatble mode", action="store_true", default=False)
    arg_parser.add_argument("--output_file", dest="OUTPUT", help="path of output file", type=str, metavar='FILE', default=sys.stdout)

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='files to read, if empty, stdin is used')
    # arg_parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    # arg_parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
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


def html_prologe(align_center=True, width=None, datatable=False):
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
        table_css = '''
    <style type="text/css">
      table {{ 
         {}
      }}
      table caption {{
         font-size:large; font-weight: bold;
      }}
      th {{
          background-color: #6495ed;
      }}
      thead tr th {{
         border-bottom: solid 1px;
       }}
    </style>
'''.format(table_css)

    text = """
<?xml version="1.0" encoding="utf-8"?>
<html>
  <!- made by csv_print_html.py -->
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
    csv_df = pd.read_csv(csv_file)

    if len(columns) > 0:
        csv_df = csv_df[columns]

    # print(csv_df.describe())

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

    html_str = html_prologe(width=None, datatable=datatable_mode)
    html_str += "<div id='tablecontainer'>"
    table_str = df_sty.render()
    table_str = re.sub(r"<table ([^>]+)>", r"<table \1 class='display nowrap' style='width:100%'>", table_str)
    html_str += table_str
    html_str += "</div>"
    html_str += html_epiloge(datatable=datatable_mode)

    print(html_str, file=output_file)
