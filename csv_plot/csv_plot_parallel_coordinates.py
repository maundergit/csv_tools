#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_plot_parallel_coordinates.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-09-02 19:12:05>
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
from pathlib import Path

import plotly.express as px
import pandas as pd

VERSION = 1.0

COLOR_TABLE = ["Inferno", "Viridis", "OrRd", "YlOrBr", "Peach", "Pinkyl", "BuGn", "solar", "haline", "matter", "algae", "amp"]


def init():
    arg_parser = argparse.ArgumentParser(description="plot parallel_coordinates chart",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:
  key colmun must have only numeric values.
  all others columns has numeric values.
  if columns has discrete values, then use '--discrete'.

  for animation column, colon ":" must be escaped by "\". ex: "Animation\:Column".
  if datetime column was used as column for animation, format of datetime should be defined.
  see datetime  Basic date and time types  Python 3.9.4 documentation https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

example:
  csv_plot_parallel_coordinates.py --format=html big_sample_arb.csv COL_0097 COL_0008,COL_0033
  csv_plot_parallel_coordinates.py --format=html --discrete big_sample_arb.csv COL_0008 COL_0006,COL_0002,COL_0023

'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument("--title", dest="TITLE", help="title of chart", type=str, metavar='TEXT', default="")
    arg_parser.add_argument("--discrete", dest="DISCRETE", help="discrete mode", action="store_true", default=False)

    arg_parser.add_argument("--ignore_key", dest="IGNKEY", help="ignore key column", action="store_true", default=False)

    arg_parser.add_argument("--color_table",
                            dest="COLTABLE",
                            help="color table for heat map, default=1",
                            choices=[str(v) for v in range(1,
                                                           len(COLOR_TABLE) + 1)],
                            default=1)
    arg_parser.add_argument("--xrange", dest="XRANGE", help="range of x", type=str, metavar='XMIN,XMAX')

    arg_parser.add_argument("--animation_column",
                            dest="ANIMATION_COL",
                            help="name of column as aimation",
                            type=str,
                            metavar='column[:datetime_format]',
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

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='csv files to read', nargs=1)
    arg_parser.add_argument('key_column', metavar='KEY', help='name of key column', nargs=1)
    arg_parser.add_argument('columns', metavar='COLUMNS', help='names of colums', nargs=1)
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    args = init()
    csv_file = args.csv_file[0]
    animation_col = args.ANIMATION_COL

    output_format = args.FORMAT
    packed_html = args.PACKED_HTML
    width = args.WIDTH
    height = args.HEIGHT
    col = int(args.COLTABLE) - 1
    output_file = args.OUTPUT
    discrete = args.DISCRETE
    ignore_key = args.IGNKEY

    if output_file is None:
        if csv_file != "-":
            output_file = Path(csv_file).stem + "_parallel." + output_format
        else:
            output_file = sys.stdout.buffer
    else:
        output_format = Path(output_file).suffix[1:]
    if csv_file == "-":
        csv_file = sys.stdin

    title = args.TITLE

    key_column = args.key_column[0]
    col_names = re.split(r'\s*,\s*', args.columns[0])

    xrange_s = args.XRANGE
    xrange = None
    if xrange_s is not None:
        xrange = re.split(r'\s*,\s*', xrange_s)
        if len(xrange) < 2:
            print("invalid '--xrange': {}".format(xrange_s), file=sys.stderr)
            exit(1)
        else:
            xrange = list(map(float, xrange))

    # Built-in Continuous Color Scales | Python | Plotly https://plotly.com/python/builtin-colorscales/#builtin-sequential-color-scales
    color_scale = COLOR_TABLE[col]

    #--- processing

    # 2D Histograms | Python | Plotly https://plotly.com/python/2D-Histogram/
    csv_df = pd.read_csv(csv_file)

    color_params = {"color_continuous_scale": color_scale}

    if ignore_key:
        fig_params = {"dimensions": col_names}
    else:
        fig_params = {"color": key_column, "dimensions": col_names}

    fig_params.update(color_params)

    if title is not None and len(title) > 0:
        fig_params["title"] = title
    if width is not None:
        fig_params["width"] = int(width)
    if height is not None:
        fig_params["height"] = int(height)
    if xrange is not None:
        fig_params["range_color"] = xrange

    if animation_col is not None:
        cvs = re.split(r"\s*(?<!\\):\s*", animation_col, maxsplit=1)
        ani_col = cvs[0]
        ani_col = re.sub(r"\\:", ":", ani_col)
        fig_params["animation_frame"] = ani_col
        if len(csv_df[ani_col].value_counts()) > 100:
            print("??error:csv_plot_bar:too many values in column for animation:{}".format(ani_col), file=sys.stderr)
            sys.exit(1)
        if len(cvs) > 1:
            t_format = cvs[1]
            csv_df = pd.to_datetime(csv_df[ani_col], format=t_format)
        else:
            if "category_orders" not in fig_params:
                fig_params["category_orders"] = {}
            fig_params["category_orders"].update({ani_col: sorted([v[0] for v in csv_df[ani_col].value_counts().items()])})

    print("""
==== plot chart from csv
input : {}
output: {}
""".format(csv_file, output_file), file=sys.stderr)
    print("parameters: {}".format(fig_params), file=sys.stderr)
    # plotly.express.parallel_coordinates  4.9.0 documentation https://plotly.com/python-api-reference/generated/plotly.express.parallel_coordinates.html
    if discrete:
        fig = px.parallel_categories(csv_df, **fig_params)
    else:
        fig = px.parallel_coordinates(csv_df, **fig_params)

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
