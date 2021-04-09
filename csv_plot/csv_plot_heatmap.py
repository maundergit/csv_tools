#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_plot_heatmap.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-08-30 09:56:44>
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

Z_HIST_FUNC_LIST = ['count', 'sum', 'avg', 'min', 'max']
COLOR_TABLE = ["Inferno", "Viridis", "OrRd", "YlOrBr", "Peach", "Pinkyl", "BuGn", "solar", "haline", "matter", "algae", "amp"]


def init():
    arg_parser = argparse.ArgumentParser(description="plot heatmap chart",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
example:
  csv_plot_heatmap.py --xrange=0,.5 --yrange=0,.5 --format=html test_plot.csv ABC001 ABC002
'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument("--title", dest="TITLE", help="title of chart", type=str, metavar='TEXT', default="")
    arg_parser.add_argument("--nbins_x", dest="NBINS_X", help="number of bins for x-axis,default=10", type=int, metavar='INT', default=10)
    arg_parser.add_argument("--nbins_y", dest="NBINS_Y", help="number of bins for y-axis,default=10", type=int, metavar='INT', default=10)
    arg_parser.add_argument("--contour", dest="CONTOUR", help="contour mode", action="store_true", default=False)
    arg_parser.add_argument("--side_hist",
                            dest="SIDE_HIST",
                            help="side histogram mode",
                            choices=['rug', 'box', 'violin', 'histogram'],
                            default=None)

    arg_parser.add_argument("--facets",
                            dest="FACETS",
                            help="names of columns to make group with csv, 'row_facet,col_facet'",
                            type=str,
                            metavar='column[,column]',
                            default=None)
    arg_parser.add_argument("--hist_func",
                            dest="Z_HIST_FUNC",
                            help="function for histogram z-axis",
                            choices=Z_HIST_FUNC_LIST,
                            default="sum")
    arg_parser.add_argument("--color_table",
                            dest="COLTABLE",
                            help="color table for heat map, default=1",
                            choices=[str(v) for v in range(1,
                                                           len(COLOR_TABLE) + 1)],
                            default=1)
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

    arg_parser.add_argument("--xrange", dest="XRANGE", help="range of x", type=str, metavar='XMIN,XMAX')
    arg_parser.add_argument("--yrange", dest="YRANGE", help="range of y", type=str, metavar='YMIN,YMAX')
    arg_parser.add_argument("--log_x", dest="LOG_X", help="log-scaled x axis", action="store_true", default=False)
    arg_parser.add_argument("--log_y", dest="LOG_Y", help="log-scaled y axis", action="store_true", default=False)
    arg_parser.add_argument("--noautoscale", dest="NOAUTOSCALE", help="not autoscale x or y for facets", action="store_false")

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
    arg_parser.add_argument('x_column', metavar='X_COLUMN', help='name of colum as x-axis', nargs=1)
    arg_parser.add_argument('y_column', metavar='Y_COLUMN', help='name of colum as y-axis', nargs=1)
    arg_parser.add_argument('z_column', metavar='Z_COLUMN', help='name of colum as z-axis', nargs="?")
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    args = init()
    csv_file = args.csv_file[0]
    output_format = args.FORMAT
    packed_html = args.PACKED_HTML
    width = args.WIDTH
    height = args.HEIGHT
    col = int(args.COLTABLE) - 1
    animation_col = args.ANIMATION_COL

    output_file = args.OUTPUT
    log_x = args.LOG_X
    log_y = args.LOG_Y
    no_auto_scale = args.NOAUTOSCALE
    contour = args.CONTOUR
    side_hist_mode = args.SIDE_HIST
    z_hist_func = args.Z_HIST_FUNC

    if output_file is None:
        if csv_file != "-":
            fopt = ""
            if side_hist_mode is not None:
                fopt = fopt + "_{}".format(side_hist_mode)
            if contour:
                fopt = fopt + "_contour"
            output_file = Path(csv_file).stem + "_heatmap_{}{}.".format(z_hist_func, fopt) + output_format
        else:
            output_file = sys.stdout.buffer
    else:
        output_format = Path(output_file).suffix[1:]
    if csv_file == "-":
        csv_file = sys.stdin

    title = args.TITLE

    x_col_name = args.x_column[0]
    y_col_name = args.y_column[0]
    if args.z_column is not None:
        z_col_name = args.z_column
    else:
        z_col_name = None

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

    nbin_x = args.NBINS_X
    nbin_y = args.NBINS_Y
    # Built-in Continuous Color Scales | Python | Plotly https://plotly.com/python/builtin-colorscales/#builtin-sequential-color-scales
    color_scale = COLOR_TABLE[col]

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

    if z_col_name is not None:
        z_params = {"z": z_col_name, "histfunc": z_hist_func}
    else:
        z_params = None

    side_hist_params = None
    color_params = {}
    if side_hist_mode is not None:
        side_hist_params = {"marginal_x": side_hist_mode, "marginal_y": side_hist_mode}
        color_params = {}
    else:
        side_hist_params = None
        color_params = {"color_continuous_scale": color_scale}
    if facet_mode:
        facet_params = {}
        if row_facet is not None and len(row_facet) > 0:
            facet_params.update(dict(facet_row=row_facet))
        if col_facet is not None and len(col_facet) > 0:
            facet_params.update(dict(facet_col=col_facet))
    else:
        facet_params = None

    nbin_params = {"nbinsx": nbin_x, "nbinsy": nbin_y}
    fig_params = {"x": x_col_name, "y": y_col_name}

    if side_hist_params is not None:
        fig_params.update(side_hist_params)
    else:
        fig_params.update(color_params)

    if facet_params is not None:
        fig_params.update(facet_params)

    fig_params.update(nbin_params)
    if z_params is not None:
        fig_params.update(z_params)
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

    figco = {}
    if csv_df[x_col_name].dtype in [str, object]:
        figco[x_col_name] = sorted(csv_df[x_col_name].value_counts().keys())
    if csv_df[y_col_name].dtype in [str, object]:
        figco[y_col_name] = sorted(csv_df[y_col_name].value_counts().keys())
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
input        : {}
output       : {}
output format: {}
""".format(csv_file, output_file, output_format),
          file=sys.stderr)
    print("parameters: {}".format(fig_params), file=sys.stderr)
    # plotly.express.density_heatmap  4.9.0 documentation https://plotly.com/python-api-reference/generated/plotly.express.density_heatmap.html
    if contour:
        fig = px.density_contour(csv_df, **fig_params)
    else:
        fig = px.density_heatmap(csv_df, **fig_params)

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
