#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_plot_line.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-09-05 10:27:42>
# Licence:
#  Copyright (c) 2021 Masaharu N. Akei
#
#  This software is released under the MIT License.
#    http://opensource.org/licenses/mit-license.php
# ----------------------------------------------------------------------
import argparse
import textwrap
import sys
import re
import json
from pathlib import Path

import plotly.express as px
import pandas as pd

VERSION = 1.0


def init():
    arg_parser = argparse.ArgumentParser(description="plot line chart",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:
  plotly.express: high-level interface for data visualization  4.9.0 documentation https://plotly.com/python-api-reference/plotly.express.html

  only x_or_y_column was given without y_columns, sequence numbers are used as x values that are generated atuomaticaly.

example:
  csv_plot_line.py --facets=COL_0006 --output=test.html big_sample_arb.csv COL_0008,COL_0033,COL_0097
  csv_plot_line.py --facets=COL_0006 --format html big_sample_arb.csv COL_0000 COL_0008,COL_0033,COL_0097
  csv_plot_line.py --output=test_line_dt.html --datetime="%Y-%m-%d %H:%M:%S" test_bar.csv dt count


'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument("--title", dest="TITLE", help="title of chart", type=str, metavar='TEXT', default="")

    arg_parser.add_argument("--facets",
                            dest="FACETS",
                            help="names of columns to make group with csv, 'row_facet,col_facet'",
                            type=str,
                            metavar='column[,column]',
                            default=None)
    arg_parser.add_argument("--category", dest="CATEG", help="name of column as category", type=str, metavar='column', default=None)
    arg_parser.add_argument("--category_orders",
                            dest="CATEG_ORDERS",
                            help="orders of elements in each category, with json format",
                            type=str,
                            metavar='JSON_STRING',
                            default=None)
    arg_parser.add_argument("--animation_column",
                            dest="ANIMATION_COL",
                            help="name of column as aimation",
                            type=str,
                            metavar='column',
                            default=None)

    arg_parser.add_argument("--datetime",
                            dest="XDATETIME",
                            help="format of x as datetime",
                            type=str,
                            metavar='DATETIME_FORMAT',
                            default=None)

    arg_parser.add_argument("--xrange", dest="XRANGE", help="range of x", type=str, metavar='XMIN,XMAX')
    arg_parser.add_argument("--yrange", dest="YRANGE", help="range of y", type=str, metavar='YMIN,YMAX')
    arg_parser.add_argument("--log_x", dest="LOG_X", help="log-scaled x axis", action="store_true", default=False)
    arg_parser.add_argument("--log_y", dest="LOG_Y", help="log-scaled y axis", action="store_true", default=False)
    arg_parser.add_argument("--noautoscale", dest="NOAUTOSCALE", help="not autoscale x or y for facets", action="store_false")
    arg_parser.add_argument("--error_x", dest="ERRORX", help="column name of error x", type=str, metavar='COLUMN')
    arg_parser.add_argument("--error_y", dest="ERRORY", help="column name of error y", type=str, metavar='COLUMN')
    # arg_parser.add_argument("--spline", dest="SPLINE", help="spline mode", action="store_true", default=False)

    arg_parser.add_argument("--output", dest="OUTPUT", help="path of output file", type=str, metavar="FILE")
    arg_parser.add_argument("--format",
                            dest="FORMAT",
                            help="format of output, default=svg",
                            choices=["svg", "png", "jpg", "json", "html"],
                            default="svg")
    arg_parser.add_argument("--packed_html",
                            dest="PACKED_HTML",
                            help="whether plotly.js is included in result html file, this is enable only for --format=html",
                            action="store_true")
    arg_parser.add_argument("--width", dest="WIDTH", help="width of output", type=int, metavar='WIDTH', default=None)
    arg_parser.add_argument("--height", dest="HEIGHT", help="height of output", type=int, metavar='HEIGHT', default=None)

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='csv files to read')
    arg_parser.add_argument('x_or_y_column',
                            metavar='X_COLUMN_OR_Y_COLUMNS',
                            help='name of x column or names of y columns with csv format')
    arg_parser.add_argument('y_columns', metavar='COLUMN[,COLUMN[,COLUMN..]]', help='names of y colums', nargs='?')
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    args = init()
    csv_file = args.csv_file
    output_format = args.FORMAT
    packed_html = args.PACKED_HTML
    width = args.WIDTH
    height = args.HEIGHT
    categ = args.CATEG
    animation_col = args.ANIMATION_COL
    output_file = args.OUTPUT
    log_x = args.LOG_X
    log_y = args.LOG_Y
    no_auto_scale = args.NOAUTOSCALE
    error_x = args.ERRORX
    error_y = args.ERRORY
    # spline_mode = args.SPLINE

    if output_file is None:
        if csv_file != "-":
            output_file = Path(csv_file).stem + "_line." + output_format
        else:
            output_file = sys.stdout.buffer
    else:
        output_format = Path(output_file).suffix[1:]
    if csv_file == "-":
        csv_file = sys.stdin

    title = args.TITLE

    x_column = args.x_or_y_column
    y_columns_s = args.y_columns
    if y_columns_s is not None:
        y_columns = re.split(r'\s*,\s*', y_columns_s)
    else:
        y_columns = re.split(r'\s*,\s*', x_column)
        x_column = None

    x_datetime_format = args.XDATETIME
    xrange_s = args.XRANGE
    xrange = None
    if xrange_s is not None:
        xrange = re.split(r'\s*,\s*', xrange_s)
        if len(xrange) < 2:
            print("invalid '--xrange': {}".format(xrange_s), file=sys.stderr)
            exit(1)
        else:
            xrange = list(map(float, xrange))
    yrange_s = args.YRANGE
    yrange = None
    if yrange_s is not None:
        yrange = re.split(r'\s*,\s*', yrange_s)
        if len(yrange) < 2:
            print("invalid '--xrange': {}".format(yrange_s), file=sys.stderr)
            exit(1)
        else:
            yrange = list(map(float, yrange))

    facets = args.FACETS
    facet_mode = False
    if facets is not None:
        facet_mode = True
        cvs = re.split(r'\s*,\s*', facets)
        if len(cvs) > 1:
            row_facet = cvs[0]
            col_facet = cvs[1]
        else:
            row_facet = cvs[0]
            col_facet = None

    categ_orders_s = args.CATEG_ORDERS
    categ_orders = {}
    if categ_orders_s is not None:
        try:
            categ_orders = json.loads(categ_orders_s)
        except json.decoder.JSONDecodeError as e:
            print("??Error: '--category_orders' has invalid format: {}".format(e), file=sys.stderr)
            print(categ_orders_s)
            sys.exit(1)

    #--- processing

    # 2D Histograms | Python | Plotly https://plotly.com/python/2D-Histogram/
    csv_df = pd.read_csv(csv_file)

    if x_column is None:
        x_column = "csv_plot_line_x"
        csv_df[x_column] = range(len(csv_df))
    elif x_datetime_format is not None:
        try:
            csv_df[x_column] = pd.to_datetime(csv_df[x_column], format=x_datetime_format)
        except Exception as e:
            print(f"??error: invalid datetime format {x_datetime_format} for {x_column}", file=sys.stderr)
            sys.exit(1)

    if facet_mode:
        facet_params = {}
        if row_facet is not None and len(row_facet) > 0:
            facet_params.update(dict(facet_row=row_facet))
        if col_facet is not None and len(col_facet) > 0:
            facet_params.update(dict(facet_col=col_facet))
    else:
        facet_params = None
    if categ is not None:
        color_params = {"color": categ}
    else:
        color_params = {}

    fig_params = {"x": x_column, "y": y_columns}
    # if spline_mode:
    #     fig_params.update({"line_shape": "vh"})

    if error_x is not None:
        fig_params.update({"error_x": error_x})
    if error_y is not None:
        fig_params.update({"error_y": error_y})

    if facet_params is not None:
        fig_params.update(facet_params)
    if len(color_params) > 0:
        fig_params.update(color_params)

    if title is not None and len(title) > 0:
        fig_params["title"] = title
    if width is not None:
        fig_params["width"] = int(width)
    if height is not None:
        fig_params["height"] = int(height)
    if xrange is not None:
        fig_params["range_x"] = xrange
    if yrange is not None:
        fig_params["range_y"] = yrange
    if log_x:
        fig_params["log_x"] = True
    if log_y:
        fig_params["log_y"] = True

    if csv_df[x_column].dtype in [str, object]:
        fig_params["category_orders"] = {x_column: sorted(csv_df[x_column].value_counts().keys())}

    if animation_col is not None:
        if "category_orders" not in fig_params:
            fig_params["category_orders"] = {}
        fig_params["animation_frame"] = animation_col
        if len(csv_df[animation_col].value_counts()) > 100:
            print("??error:csv_plot_bar:too many values in column for animation:{}".format(animation_col), file=sys.stderr)
            sys.exit(1)
        fig_params["category_orders"].update({animation_col: sorted([v[0] for v in csv_df[animation_col].value_counts().items()])})

    if len(categ_orders) > 0:
        if "category_orders" in fig_params:
            fig_params["category_orders"].update(categ_orders)
        else:
            fig_params["category_orders"] = categ_orders

    print("""
==== plot chart from csv
input : {}
output: {}
""".format(csv_file, output_file), file=sys.stderr)
    print("parameters: {}".format(fig_params), file=sys.stderr)
    # plotly.express.line  4.9.0 documentation https://plotly.com/python-api-reference/generated/plotly.express.line.html
    fig = px.line(csv_df, **fig_params)

    if facet_mode:
        if not no_auto_scale and (row_facet is not None and len(row_facet) > 0) and (col_facet is None or len(col_facet) == 0):
            fig.update_yaxes(matches=None)
        elif not no_auto_scale and (row_facet is None or len(row_facet) > 0) and (col_facet is not None and len(col_facet) > 0):
            fig.update_xaxes(matches=None)

    if output_format == "json":
        if output_file == sys.stdout.buffer:
            output_file = sys.stdout
        fig.write_json(output_file)
    elif output_format == "html":
        if output_file == sys.stdout.buffer:
            output_file = sys.stdout
        if packed_html:
            fig.write_html(output_file, include_plotlyjs=True, full_html=True)
        else:
            fig.write_html(output_file, include_plotlyjs='directory', full_html=True)
    else:
        fig.write_image(output_file, format=output_format)
