#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_plot_quiver.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-10-11 11:41:09>
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

import scipy.interpolate as scii
import numpy as np
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go

VERSION = 1.0


def init():
    arg_parser = argparse.ArgumentParser(description="plot quiver chart",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:
  Quiver Plots | Python | Plotly https://plotly.com/python/quiver-plots/


example:
  csv_plot_quiver.py --title="sample of quiver chart" --format=html test_quiver.csv X Y U V
  csv_plot_quiver.py --title="sample of quiver chart" --streamline=10,10 --format=html test_quiver.csv X Y U V

'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument("--title", dest="TITLE", help="title of chart", type=str, metavar='TEXT', default="")
    arg_parser.add_argument("--x_title", dest="X_TITLE", help="title of x axis", type=str, metavar='TEXT', default="")
    arg_parser.add_argument("--y_title", dest="Y_TITLE", help="title of y axis", type=str, metavar='TEXT', default="")

    arg_parser.add_argument("--arrow_size", dest="ASIZE", help="size factor of arrow,[0,1]", type=float, default=.25)
    arg_parser.add_argument("--line_width", dest="LWIDTH", help="width of line of arrow", type=float, default=2)
    arg_parser.add_argument("--streamline", dest="STREAM", help="[exp]stream line mode", type=str, metavar="NGRIDX,NGRIDY", default=None)

    arg_parser.add_argument("--xrange", dest="XRANGE", help="range of x", type=str, metavar='XMIN,XMAX')
    arg_parser.add_argument("--yrange", dest="YRANGE", help="range of y", type=str, metavar='YMIN,YMAX')
    arg_parser.add_argument("--log_x", dest="LOG_X", help="log-scaled x axis", action="store_true", default=False)
    arg_parser.add_argument("--log_y", dest="LOG_Y", help="log-scaled y axis", action="store_true", default=False)

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
    arg_parser.add_argument('u_column', metavar='U_COLUMN', help='name of u column')
    arg_parser.add_argument('v_column', metavar='V_COLUMN', help='name of v column')
    args = arg_parser.parse_args()
    return args


def convert_griddata(x_data, y_data, u_data, v_data, n_of_gridx, n_of_gridy):
    """array to grid data with interplation

    :param x_data: 1d array
    :param y_data: 1d array
    :param u_data: 1d array
    :param v_data: 1d array
    :param n_of_gridx: number of grid for x
    :param n_of_gridy: number of grid for y
    :returns: 
    :rtype: 

    """
    xy = np.array([x_data, y_data]).T
    x = np.linspace(min(x_data), max(x_data), n_of_gridx)
    y = np.linspace(min(y_data), max(y_data), n_of_gridy)
    GY, GX = np.meshgrid(x, y)
    # scipy.interpolate.griddata  SciPy v1.5.3 Reference Guide https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html
    # g_method = 'linear'
    # g_method = 'cubic'
    g_method = 'nearest'
    GU = scii.griddata(xy, u_data, (GX, GY), method=g_method, fill_value=0)
    GV = scii.griddata(xy, v_data, (GX, GY), method=g_method, fill_value=0)
    return x, y, GX, GY, GU, GV


if __name__ == "__main__":
    args = init()
    csv_file = args.csv_file
    output_format = args.FORMAT
    packed_html = args.PACKED_HTML
    width = args.WIDTH
    height = args.HEIGHT
    arrow_size = args.ASIZE
    line_width = args.LWIDTH
    streamline_mode = args.STREAM

    output_file = args.OUTPUT
    log_x = args.LOG_X
    log_y = args.LOG_Y

    if output_file is None:
        if csv_file != "-":
            if streamline_mode is not None:
                output_file = Path(csv_file).stem + "_streamline." + output_format
            else:
                output_file = Path(csv_file).stem + "_quiver." + output_format
        else:
            output_file = sys.stdout.buffer
    else:
        output_format = Path(output_file).suffix[1:]
    if csv_file == "-":
        csv_file = sys.stdin

    x_column = args.x_column
    y_column = args.y_column
    u_column = args.u_column
    v_column = args.v_column

    title = args.TITLE
    x_title = args.X_TITLE
    if len(x_title) == 0:
        x_title = x_column
    y_title = args.Y_TITLE
    if len(y_title) == 0:
        y_title = y_column

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

    ngridx = 0
    ngridy = 0
    if streamline_mode is not None:
        cvs = re.split(r"\s*,\s*", streamline_mode)
        ngridx = int(cvs[0])
        ngridy = int(cvs[1])

    #--- processing

    # 2D Histograms | Python | Plotly https://plotly.com/python/2D-Histogram/
    csv_df = pd.read_csv(csv_file)

    x_column_data = csv_df[x_column].values
    y_column_data = csv_df[y_column].values
    u_column_data = csv_df[u_column].values
    v_column_data = csv_df[v_column].values

    fig_params = {
        "x": x_column_data,
        "y": y_column_data,
        "u": u_column_data,
        "v": v_column_data,
        "scale": arrow_size,
        "line_width": line_width
    }

    if width is not None:
        fig_params["width"] = int(width)
    if height is not None:
        fig_params["height"] = int(height)

    # for layout
    layout_fig_params = {}
    # Setting the Font, Title, Legend Entries, and Axis Titles | Python | Plotly https://plotly.com/python/figure-labels/
    if title is not None and len(title) > 0:
        layout_fig_params["title"] = {"text": title, "x": 0.5, "y": 0.9, "xanchor": "center", "yanchor": "top"}
    if x_title is not None and len(x_title) > 0:
        layout_fig_params["xaxis_title"] = x_title
    if y_title is not None and len(y_title) > 0:
        layout_fig_params["yaxis_title"] = y_title

    # for axis
    x_fig_params = {}
    if xrange is not None:
        x_fig_params["range"] = xrange
    if log_x:
        x_fig_params["type"] = "log"
    y_fig_params = {}
    if yrange is not None:
        y_fig_params["range"] = yrange
    if log_y:
        y_fig_params["type"] = "log"

    print("""
==== plot chart from csv
input : {}
output: {}
""".format(csv_file, output_file), file=sys.stderr)
    # print("parameters: {}".format(fig_params), file=sys.stderr)
    # plotly.figure_factory.create_quiver  4.11.0 documentation https://plotly.github.io/plotly.py-docs/generated/plotly.figure_factory.create_quiver.html
    # plotly.figure_factory.create_streamline  4.12.0 documentation https://plotly.com/python-api-reference/generated/plotly.figure_factory.create_streamline.html#plotly.figure_factory.create_streamline
    if ngridx > 0 and ngridy > 0:
        x, y, GX, GY, GU, GV = convert_griddata(x_column_data, y_column_data, u_column_data, v_column_data, ngridx, ngridy)
        del fig_params["x"]
        del fig_params["y"]
        del fig_params["u"]
        del fig_params["v"]
        del fig_params["scale"]
        fig = ff.create_streamline(x, y, GU, GV, **fig_params)
    else:
        fig = ff.create_quiver(**fig_params)

    if len(layout_fig_params) > 0:
        fig.update_layout(**layout_fig_params)
    # Axes | Python | Plotly https://plotly.com/python/axes/#setting-the-range-of-axes-manually
    if len(x_fig_params) > 0:
        fig.update_xaxes(**x_fig_params)
    if len(y_fig_params) > 0:
        fig.update_yaxes(**y_fig_params)

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
