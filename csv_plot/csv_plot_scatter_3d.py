#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_plot_scatter_3d.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-10-09 09:52:21>
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
    arg_parser = argparse.ArgumentParser(description="plot 3d scatter chart",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:
  plotly.express.scatter_3d  4.11.0 documentation https://plotly.com/python-api-reference/generated/plotly.express.scatter_3d.html

example:
  csv_plot_scatter_3d.py --format=html --category=COL_0006 big_sample_arb.csv COL_0008 COL_0033 COL_0097
  csv_plot_scatter_3d.py --format=html --category=COL_0006 --size_column=COL_0107 big_sample_arb.csv COL_0008 COL_0033 COL_0097

'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument("--title", dest="TITLE", help="title of chart", type=str, metavar='TEXT', default="")

    arg_parser.add_argument("--category", dest="CATEG", help="name of column as category", type=str, metavar='column', default=None)
    arg_parser.add_argument("--category_orders",
                            dest="CATEG_ORDERS",
                            help="orders of elements in each category, with json format",
                            type=str,
                            metavar='JSON_STRING',
                            default=None)
    arg_parser.add_argument("--size_column",
                            dest="SIZE_COL",
                            help="name of column as size of symbol",
                            type=str,
                            metavar='column',
                            default=None)
    arg_parser.add_argument("--animation_column",
                            dest="ANIMATION_COL",
                            help="name of column as aimation",
                            type=str,
                            metavar='column',
                            default=None)

    arg_parser.add_argument("--xrange", dest="XRANGE", help="range of x", type=str, metavar='XMIN,XMAX')
    arg_parser.add_argument("--yrange", dest="YRANGE", help="range of y", type=str, metavar='YMIN,YMAX')
    arg_parser.add_argument("--zrange", dest="ZRANGE", help="range of z", type=str, metavar='ZMIN,ZMAX')
    arg_parser.add_argument("--log_x", dest="LOG_X", help="log-scaled x axis", action="store_true", default=False)
    arg_parser.add_argument("--log_y", dest="LOG_Y", help="log-scaled y axis", action="store_true", default=False)
    arg_parser.add_argument("--log_z", dest="LOG_Z", help="log-scaled z axis", action="store_true", default=False)
    arg_parser.add_argument("--error_x", dest="ERRORX", help="column name of error x", type=str, metavar='COLUMN')
    arg_parser.add_argument("--error_y", dest="ERRORY", help="column name of error y", type=str, metavar='COLUMN')
    arg_parser.add_argument("--error_z", dest="ERRORZ", help="column name of error z", type=str, metavar='COLUMN')

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
    arg_parser.add_argument('x_column', metavar='X_COLUMN', help='name of x column')
    arg_parser.add_argument('y_column', metavar='Y_COLUMN', help='name of y column')
    arg_parser.add_argument('z_column', metavar='Z_COLUMN', help='name of z column')
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    color_limit = 10

    args = init()
    csv_file = args.csv_file
    output_format = args.FORMAT
    packed_html = args.PACKED_HTML
    width = args.WIDTH
    height = args.HEIGHT
    categ = args.CATEG
    size_col = args.SIZE_COL
    animation_col = args.ANIMATION_COL

    output_file = args.OUTPUT
    log_x = args.LOG_X
    log_y = args.LOG_Y
    log_z = args.LOG_Z
    error_x = args.ERRORX
    error_y = args.ERRORY
    error_z = args.ERRORZ
    # spline_mode = args.SPLINE

    if output_file is None:
        if csv_file != "-":
            output_file = Path(csv_file).stem + "_scatter_3d." + output_format
        else:
            output_file = sys.stdout.buffer
    else:
        output_format = Path(output_file).suffix[1:]
    if csv_file == "-":
        csv_file = sys.stdin

    title = args.TITLE

    x_column = args.x_column
    y_column = args.y_column
    z_column = args.z_column

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
            print("invalid '--yrange': {}".format(yrange_s), file=sys.stderr)
            exit(1)
        else:
            yrange = list(map(float, yrange))
    zrange_s = args.ZRANGE
    zrange = None
    if zrange_s is not None:
        zrange = re.split(r'\s*,\s*', zrange_s)
        if len(zrange) < 2:
            print("invalid '--zrange': {}".format(zrange_s), file=sys.stderr)
            exit(1)
        else:
            zrange = list(map(float, zrange))

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

    if categ is not None:
        csv_df[categ] = csv_df[categ].astype(str, errors="ignore")
        if len(list(csv_df[categ].value_counts().items())) > color_limit:
            color_params = {"symbol": categ}
        else:
            color_params = {"color": categ, "symbol": categ}
    else:
        color_params = {}
    if size_col is not None:
        color_params.update({"size": size_col})

    fig_params = {"x": x_column, "y": y_column, "z": z_column}
    # if spline_mode:
    #     fig_params.update({"line_shape": "vh"})

    if error_x is not None:
        fig_params.update({"error_x": error_x})
    if error_y is not None:
        fig_params.update({"error_y": error_y})
    if error_z is not None:
        fig_params.update({"error_z": error_z})

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
    if zrange is not None:
        fig_params["range_z"] = zrange
    if log_x:
        fig_params["log_x"] = True
    if log_y:
        fig_params["log_y"] = True
    if log_z:
        fig_params["log_z"] = True

    figco = {}
    if csv_df[x_column].dtype in [str, object]:
        figco[x_column] = sorted(csv_df[x_column].value_counts().keys())
    if csv_df[y_column].dtype in [str, object]:
        figco[y_column] = sorted(csv_df[y_column].value_counts().keys())
    if csv_df[z_column].dtype in [str, object]:
        figco[z_column] = sorted(csv_df[z_column].value_counts().keys())
    if len(figco) > 0:
        fig_params["category_orders"] = figco

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
    # plotly.express.scatter_3d  4.11.0 documentation https://plotly.com/python-api-reference/generated/plotly.express.scatter_3d.html
    fig = px.scatter_3d(csv_df, **fig_params)
    fig.update_layout(coloraxis_colorbar=dict(yanchor="top", y=1, x=0, ticks="outside"))

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
