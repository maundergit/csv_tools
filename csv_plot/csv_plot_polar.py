#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_plot_polar.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-09-06 10:49:53>
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
    arg_parser = argparse.ArgumentParser(description="plot polar chart",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:


example:
  import plotly.express as px
  df = px.data.wind()
  df.to_csv("test_polar.csv")

  head test_polar.csv
  ,direction,strength,frequency
  0,N,0-1,0.5
  1,NNE,0-1,0.6
  2,NE,0-1,0.5
  3,ENE,0-1,0.4

  # for string dierction, use '--start_angle=90 --direction="clockwise"'
  csv_plot_polar.py --format=html --category=strength --start_angle=90 --direction="clockwise" \
                    test_polar.csv frequency direction frequency
  csv_plot_polar.py --format=html --type=line --category=strength --line_close --line_shape=spline \
                    --start_angle=90 --direction="clockwise" test_polar.csv frequency direction frequency

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
    arg_parser.add_argument("--rrange", dest="RRANGE", help="range of radius", type=str, metavar='RMIN,RMAX')
    arg_parser.add_argument("--thrange", dest="THRANGE", help="range of theta", type=str, metavar='THMIN,THMAX')
    arg_parser.add_argument("--log_r", dest="LOG_R", help="log-scaled radius", action="store_true", default=False)
    arg_parser.add_argument("--direction",
                            dest="DIRECTION",
                            help="direction of rotation",
                            choices=["counterclockwise", "clockwise"],
                            type=str,
                            default="counterclockwise")
    arg_parser.add_argument("--start_angle", dest="START_ANGLE", help="angle for starting plot [deg]", type=float, default=0)
    arg_parser.add_argument("--clock",
                            dest="CLOCK",
                            help="equal to --start_angle=90 --direction='clockwise': '--start_angle'and '--direction' are ignored.",
                            action="store_true",
                            default=False)

    arg_parser.add_argument("--type", dest="TYPE", help="chart type", choices=["scatter", "line", "bar"], type=str, default="scatter")
    arg_parser.add_argument("--line_close",
                            dest="LINE_CLOSE",
                            help="line closing mode, available for only line chart",
                            action="store_true",
                            default=False)
    arg_parser.add_argument("--line_shape",
                            dest="LINE_SHAPE",
                            help="line shape, available for only line chart",
                            choices=["linear", "spline"],
                            type=str,
                            default="linear")
    arg_parser.add_argument("--animation_column",
                            dest="ANIMATION_COL",
                            help="name of column as aimation",
                            type=str,
                            metavar='column',
                            default=None)

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
    arg_parser.add_argument('r_column', metavar='R_COLUMN', help='name of colum as radius')
    arg_parser.add_argument('theta_column', metavar='THETA_COLUMN', help='name of colum as theta')
    arg_parser.add_argument('weight_column', metavar='WEIGHT_COLUMN', help='name of colum as weight', nargs="?")
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
    log_r = args.LOG_R
    chart_type = args.TYPE
    line_close = args.LINE_CLOSE
    line_shape = args.LINE_SHAPE
    th_direction = args.DIRECTION
    start_angle = args.START_ANGLE

    if args.CLOCK:
        th_direction = "clockwise"
        start_angle = 90

    if output_file is None:
        if csv_file != "-":
            output_file = Path(csv_file).stem + "_polar_{}.".format(chart_type) + output_format
        else:
            output_file = sys.stdout.buffer
    else:
        output_format = Path(output_file).suffix[1:]
    if csv_file == "-":
        csv_file = sys.stdin

    title = args.TITLE

    r_col_name = args.r_column
    theta_col_name = args.theta_column
    weight_col_name = args.weight_column

    rrange_s = args.RRANGE
    rrange = None
    if rrange_s is not None:
        rrange = re.split(r'\s*,\s*', rrange_s)
        if len(rrange) < 2:
            print("invalid '--xrange': {}".format(rrange_s), file=sys.stderr)
            exit(1)
        else:
            rrange = list(map(float, rrange))
    thrange_s = args.THRANGE
    thrange = None
    if thrange_s is not None:
        thrange = re.split(r'\s*,\s*', thrange_s)
        if len(thrange) < 2:
            print("invalid '--yrange': {}".format(thrange_s), file=sys.stderr)
            exit(1)
        else:
            thrange = list(map(float, thrange))

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
    csv_df = pd.read_csv(csv_file)

    fig_params = {"r": r_col_name, "theta": theta_col_name, "start_angle": start_angle, "direction": th_direction}
    line_params = {"line_close": line_close, "line_shape": line_shape}
    scatter_params = {}
    if categ is not None:
        scatter_params.update({"symbol": categ})
    if weight_col_name is not None:
        scatter_params.update({"size": weight_col_name})

    if categ is not None:
        color_params = {"color": categ}
    else:
        color_params = {}

    if len(color_params) > 0:
        fig_params.update(color_params)
    if title is not None and len(title) > 0:
        fig_params["title"] = title
    if width is not None:
        fig_params["width"] = int(width)
    if height is not None:
        fig_params["height"] = int(height)
    if rrange is not None:
        fig_params["range_r"] = rrange
    if thrange is not None:
        fig_params["range_theta"] = thrange
    if log_r:
        fig_params["log_r"] = True

    if chart_type == "scatter":
        fig_params.update(scatter_params)
    elif chart_type == "line":
        fig_params.update(line_params)

    figco = {}
    if csv_df[r_col_name].dtype in [str, object]:
        figco[r_col_name] = sorted(csv_df[r_col_name].value_counts().keys())
    if csv_df[theta_col_name].dtype in [str, object]:
        figco[theta_col_name] = sorted(csv_df[theta_col_name].value_counts().keys())
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
    if chart_type == "scatter":
        # plotly.express.scatter_polar  4.9.0 documentation https://plotly.com/python-api-reference/generated/plotly.express.scatter_polar.html
        fig = px.scatter_polar(csv_df, **fig_params)
    elif chart_type == "bar":
        # plotly.express.bar_polar  4.10.0 documentation https://plotly.com/python-api-reference/generated/plotly.express.bar_polar.html
        fig = px.bar_polar(csv_df, **fig_params)
    else:
        # plotly.express.line_polar  4.9.0 documentation https://plotly.com/python-api-reference/generated/plotly.express.line_polar.html
        fig = px.line_polar(csv_df, **fig_params)

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
