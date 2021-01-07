#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_plot_annotated_heatmap.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-10-31 08:16:53>
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

import numpy as np
import plotly.figure_factory as pff
import pandas as pd

VERSION = 1.0

COLOR_TABLE = ["Inferno", "Viridis", "OrRd", "YlOrBr", "Peach", "Pinkyl", "BuGn", "solar", "haline", "matter", "algae", "amp"]


def init():
    # argparse --- コマンドラインオプション、引数、サブコマンドのパーサー  Python 3.8.5 ドキュメント https://docs.python.org/ja/3/library/argparse.html
    arg_parser = argparse.ArgumentParser(description="create heatmap chart for x-y matrix data",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:
  The input data must have the csv format, you may select numerical columns as X and optionaly column for labels of rows as Y.
  If columns of X and Y was not given, all elements are used as numerical values.
  When you want to select rows, you may use '--query'.

  Labels for X-axis are made from names of columns. labels for Y-axis are row number for deault or contents in Y column if given.

example:
  csv_plot_annotated_heatmap.py --format=html --x=B,C,D,E --y=A --show_scale --x_title=XAXIS --y_title=YAXIS test_annotated_heatmap.csv
  csv_plot_annotated_heatmap.py --format=html --x=B,C,D,E --y=A --show_scale --x_title=XAXIS --y_title=YAXIS --query="B>=10" test_annotated_heatmap.csv

'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument("--title", dest="TITLE", help="title of chart", type=str, metavar='TEXT', default="")
    arg_parser.add_argument("--x_title", dest="X_TITLE", help="title of x axis", type=str, metavar='TEXT', default="")
    arg_parser.add_argument("--y_title", dest="Y_TITLE", help="title of y axis", type=str, metavar='TEXT', default="")

    arg_parser.add_argument("--color_table",
                            dest="COLTABLE",
                            help="color table for heat map, default=1",
                            choices=[str(v) for v in range(1,
                                                           len(COLOR_TABLE) + 1)],
                            default=1)

    arg_parser.add_argument("--x", dest="X_COLUMNS", help="names of columns for x", type=str, metavar='COLUMN[,COLUMN...]')
    arg_parser.add_argument("--y", dest="Y_COLUMN", help="name of column for Y", type=str, metavar='COLUMN')
    arg_parser.add_argument("--zrange",
                            dest="ZRANGE",
                            help="range of Z, this is used for only color scale.",
                            type=str,
                            metavar='ZMIN,ZMAX')
    arg_parser.add_argument("--log_z", dest="LOG_Z", help="log-scaled Z axis", action="store_true", default=False)

    arg_parser.add_argument("--query", dest="QUERY", help="query string to select rows", type=str, metavar='QUERY')

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
    arg_parser.add_argument("--show_scale", dest="SSCALE", help="show scale", action='store_true', default=False)

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='csv files to read', nargs=1)
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    npts_limit = 100

    args = init()
    csv_file = args.csv_file[0]
    output_format = args.FORMAT
    packed_html = args.PACKED_HTML
    width = args.WIDTH
    height = args.HEIGHT
    show_scale = args.SSCALE
    col = int(args.COLTABLE) - 1
    title = args.TITLE
    x_title = args.X_TITLE
    y_title = args.Y_TITLE

    df_query = args.QUERY

    output_file = args.OUTPUT
    log_z = args.LOG_Z

    if output_file is None:
        if csv_file != "-":
            output_file = Path(csv_file).stem + "_annotated_heatmap." + output_format
        else:
            output_file = sys.stdout.buffer
    else:
        output_format = Path(output_file).suffix[1:]
    if csv_file == "-":
        csv_file = sys.stdin

    x_col_names_s = args.X_COLUMNS
    x_col_names = None
    if x_col_names_s is not None:
        x_col_names = re.split(r"\s*,\s*", x_col_names_s)

    y_col_name = args.Y_COLUMN

    zrange_s = args.ZRANGE
    zrange = None
    if zrange_s is not None:
        zrange = re.split(r'\s*,\s*', zrange_s)
        if len(zrange) < 2:
            print("invalid '--zrange': {}".format(zrange_s), file=sys.stderr)
            sys.exit(1)
        else:
            zrange = list(map(float, zrange))

    # Built-in Continuous Color Scales | Python | Plotly https://plotly.com/python/builtin-colorscales/#builtin-sequential-color-scales
    color_scale = COLOR_TABLE[col]

    fig_ul_params = {}
    if len(title) > 0:
        fig_ul_params["title"] = title
    if len(x_title) > 0:
        fig_ul_params["xaxis_title"] = x_title
    if len(y_title) > 0:
        fig_ul_params["yaxis_title"] = y_title
    else:
        fig_ul_params["yaxis_title"] = y_col_name

    #--- processing

    csv_df = pd.read_csv(csv_file)

    if df_query is not None:
        try:
            csv_df.query(df_query, engine='python', inplace=True)
        except TypeError as e:
            print("??Error:csv_plot_annotated_heatmap:query '{}':{}".format(df_query, e), file=sys.stderr)
            print("-- data types in csv", file=sys.stderr)
            print(textwrap.indent(str(csv_df.dtypes), ">> "), file=sys.stderr)
            sys.exit(1)

    fig_params = {"colorscale": color_scale, "showscale": show_scale}
    y_col = []
    if y_col_name is not None:
        y_col = csv_df[y_col_name].to_numpy(copy=True).tolist()
        csv_df.drop(y_col_name, axis=1, inplace=True)
        fig_params["y"] = y_col

    if x_col_names is None:
        z_array = csv_df.to_numpy(copy=True)
    else:
        z_array = csv_df[x_col_names].to_numpy(copy=True)
        fig_params["x"] = x_col_names

    if z_array.shape[0] > npts_limit or z_array.shape[1] > npts_limit:
        print("#warn:csv_plot_annotated_heatmap: number of columns is too many:{}".format(z_array.shape))
    if z_array.dtype == np.dtype('object'):
        print("??Error:csv_plot_annotated_heatmap:invalid datas: values must be decimal format. you may use '--x'.", file=sys.stderr)
        print(z_array)
        sys.exit(1)

    if width is not None:
        fig_params["width"] = int(width)
    if height is not None:
        fig_params["height"] = int(height)
    if log_z:
        fig_params["annotation_text"] = z_array.copy().tolist()
        z_array = np.log10(z_array)
        if zrange is not None:
            fig_params["zmin"] = np.log10(float(zrange[0]))
            fig_params["zmax"] = np.log10(float(zrange[1]))
    else:
        if zrange is not None:
            fig_params["zmin"] = float(zrange[0])
            fig_params["zmax"] = float(zrange[1])

    print("""
==== plot chart from csv
input        : {}
output       : {}
output format: {}
""".format(csv_file, output_file, output_format),
          file=sys.stderr)
    print("parameters: {}".format(fig_params), file=sys.stderr)
    # Annotated Heatmaps | Python | Plotly https://plotly.com/python/annotated-heatmap/
    # plotly.figure_factory.create_annotated_heatmap  4.12.0 documentation https://plotly.com/python-api-reference/generated/plotly.figure_factory.create_annotated_heatmap.html#plotly.figure_factory.create_annotated_heatmap
    # plotly.graph_objects.Heatmap  4.12.0 documentation https://plotly.com/python-api-reference/generated/plotly.graph_objects.Heatmap.html#plotly.graph_objects.Heatmap
    fig = pff.create_annotated_heatmap(z_array, **fig_params)

    if len(fig_ul_params) > 0:
        fig.update_layout(**fig_ul_params)

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
