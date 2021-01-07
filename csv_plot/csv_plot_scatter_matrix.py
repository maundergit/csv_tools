#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_plot_scatter_matrix.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-08-30 15:06:06>
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
    arg_parser = argparse.ArgumentParser(description="plot scatter matrix",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
example:
  csv_plot_scatter_matrix.py --columns="ABC001","ABC002","ABC003" --category="ABC004" --output=test.png test_plot.csv
'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument("--title", dest="TITLE", help="title of chart", type=str, metavar='TEXT', default="")
    arg_parser.add_argument("--columns",
                            dest="COLUMNS",
                            help="list of names of columns with csv",
                            type=str,
                            metavar='COLUMNS,COLUMNS[,COLUMNS...]',
                            required=True)
    arg_parser.add_argument("--category", dest="SYMBOL", help="name of column to make group", type=str, metavar='COLUMN', default=None)
    arg_parser.add_argument("--category_orders",
                            dest="CATEG_ORDERS",
                            help="orders of elements in each category, with json format",
                            type=str,
                            metavar='JSON_STRING',
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
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":

    color_limit = 10

    args = init()
    csv_file = args.csv_file[0]

    output_format = args.FORMAT
    width = args.WIDTH
    height = args.HEIGHT
    output_file = args.OUTPUT
    packed_html = args.PACKED_HTML

    if output_file is None:
        if csv_file != "-":
            output_file = Path(csv_file).stem + "_scatter_matrix." + output_format
        else:
            output_file = sys.stdout.buffer
    else:
        output_format = Path(output_file).suffix[1:]
    if csv_file == "-":
        csv_file = sys.stdin

    title = args.TITLE
    dimensions = re.split(r"\s*,\s*", args.COLUMNS)
    symbol = args.SYMBOL

    # Built-in Continuous Color Scales | Python | Plotly https://plotly.com/python/builtin-colorscales/#builtin-sequential-color-scales
    color_scales = ["Inferno", "Viridis", "OrRd", "YlOrBr", "BuGn"]
    color_scale = color_scales[4]

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

    fig_params = {"dimensions": dimensions, "opacity": 1.0}

    # 2D Histograms | Python | Plotly https://plotly.com/python/2D-Histogram/
    csv_df = pd.read_csv(csv_file)

    if symbol is not None:
        csv_df[symbol] = csv_df[symbol].astype(str, errors="ignore")
        if len(list(csv_df[symbol].value_counts().items())) > color_limit:
            fig_params.update({"symbol": symbol})
        else:
            fig_params.update({"symbol": symbol, "color": symbol})

    if title is not None and len(title) > 0:
        fig_params["title"] = title
    if width is not None:
        fig_params["width"] = int(width)
    if height is not None:
        fig_params["height"] = int(height)

    figco = {}
    for col in dimensions:
        if csv_df[col].dtype in [str, object]:
            figco[col] = sorted(csv_df[col].value_counts().keys())
    if len(figco) > 0:
        fig_params["category_orders"] = figco
    if len(categ_orders) > 0:
        if "category_orders" in fig_params:
            fig_params["category_orders"].update(categ_orders)
        else:
            fig_params["category_orders"] = categ_orders

    print("""
==== plot chart from csv
input     : {}
output    : {}
""".format(csv_file, output_file), file=sys.stderr)
    print("parameters: {}".format(fig_params), file=sys.stderr)

    # Scatterplot Matrix | Python | Plotly https://plotly.com/python/splom/
    # plotly.express.scatter_matrix  4.9.0 documentation https://plotly.github.io/plotly.py-docs/generated/plotly.express.scatter_matrix.html
    fig = px.scatter_matrix(csv_df, **fig_params)
    fig.update_layout(coloraxis_colorbar=dict(yanchor="top", y=1, x=0, ticks="outside"))

    fig.update_traces(diagonal_visible=False)

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
