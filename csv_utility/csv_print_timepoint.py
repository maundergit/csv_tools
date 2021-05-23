#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_print_timepoint.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2021 by m.na.akei
# Time-stamp:   <2021-05-21 18:19:27>
# Licence:
# ----------------------------------------------------------------------
import argparse
import fileinput
import textwrap
import sys

import re
from pathlib import Path
import tempfile

import subprocess
from io import StringIO, BytesIO

from lxml import etree
import pandas as pd

sys.path.insert(0, format(Path(__file__).parent))
from csv_print_html_tl import make_gantt
from csv_print_timeline_trim_svg import add_style, add_script, trim_svg_string

VERSION = 1.0


def init():
    arg_parser = argparse.ArgumentParser(description="make timepoint chart of datetime information in csv data",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:
  there must be 'csv_print_html_tl.py' and 'csv_print_timeline_trim_svg.py' must be the same directory.

  this script reuires 'plantuml' command, newer than '2021.6'.  see 'https://plantuml.com/ja/download'.
  if you did not have 'plantuml', then use 'apt install plantuml' and '/usr/share/plantuml/plantuml.jar' must be replaceed latest jar.
  then '--plantuml_command' may be usefull.

  using '--group_column', each record will be plotted as milestone at poistion, that was grouped by the value.

  if '--tag_column' was not defined, the format:'id_nn' is used as tag text.
  when '--tag_column' was defined, the value will be plotted as tag text of the milestone.
  if some records have the same value in the tag column, tag text with serial number will be used..

  if there were many records in the same day and the view had too large height, '--shrink_by_day' may be used.

  after editing plantuml file, '--only_pu' may be used.
  if '--only_pu' was given, other options is ignored and only msaking/triming svg are done.

  used tag text is stored into '*_tags.csv'. this may be used to do following.
    HTML=test.html
    INPUT_TAGS=csv_print_timepoint_sample0_tags.csv
    INPUT_SVG=csv_print_timepoint_sample0.svg
    OUTPUT_SVG=linked_to_html.svg
    sed "$(csvcut -c id_name ${INPUT_TAGS}|sed '1d'|while read TAG;do echo "s/${TAG}/<a href='${HTML}#${TAG}'>${TAG}<\/a>/g;";done)"  ${INPUT_SVG} > ${OUTPUT_SVG}

example:
  csv_print_timepoint.py --group_column=group csv_print_timepoint_sample0.csv datetime
  csv_print_timepoint.py --group_column=group --tag_column header csv_print_timepoint_sample0.csv datetime
  csv_print_timepoint.py --group_column=group --tag_column header --shrink_by_day csv_print_timepoint_sample0.csv datetime
  csv_print_timepoint.py --only_pu csv_print_timepoint_sample0.pu

'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument("--title", dest="TITLE", help="title string", type=str, metavar='TEXT', default=None)
    arg_parser.add_argument("--datetime_format",
                            dest="DFORMAT",
                            help="format of datetime column,default='%%Y-%%m-%%d %%H:%%M:%%S'",
                            type=str,
                            metavar='DATETIME_FORMAT',
                            default="%Y-%m-%d %H:%M:%S")
    arg_parser.add_argument("--group_column", dest="GCOLUMN", help="column of group", type=str, metavar='COLUMN', default=None)
    arg_parser.add_argument("--tag_column", dest="TCOLUMN", help="column of tag text", type=str, metavar='COLUMN', default=None)

    arg_parser.add_argument("--shrink_by_day", dest="SHRINK", help="summarize by day", action="store_true", default=False)

    arg_parser.add_argument("--only_pu",
                            dest="ONLY_PU",
                            help="plantuml file as input, instead of csv file",
                            action="store_true",
                            default=False)

    arg_parser.add_argument("--plantuml_command",
                            dest="PCOMMAND",
                            help="path of command of plantuml",
                            type=str,
                            metavar='COMMAND',
                            default="plantuml")

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='files to read, if empty, stdin is used')
    arg_parser.add_argument('datetime_column', metavar='DATETIME_COLUMN', nargs="?", help="column of datetime")
    args = arg_parser.parse_args()
    return args


def triming_svg(svg_string, pu_groups):
    svg_parser = etree.XMLParser(ns_clean=True, encoding="utf8")
    svg_tree = etree.parse(BytesIO(svg_string.encode("utf-8")), svg_parser)
    svg_root = svg_tree.getroot()
    xml_ns = {"svg": "http://www.w3.org/2000/svg"}
    add_style(svg_root, pu_groups)
    add_script(svg_root)
    svg_string = etree.tostring(svg_root, encoding="utf8", method="xml")
    svg_string = svg_string.decode('utf8')
    svg_string = trim_svg_string(svg_string)
    return svg_string


def make_svg(pu_text, output_svg, pu_groups, plantuml_cmd):
    ret = subprocess.run([plantuml_cmd, "-p", "-tsvg"], capture_output=True, input=pu_text, encoding="utf-8")
    if ret.returncode != 0:
        mes = f"??error:csv_print_timepoint: {plantuml_cmd} was not found"
        print(mes, file=sys.stderr)
        sys, exit(1)
    svg_string = ret.stdout
    svg_string = triming_svg(svg_string, pu_groups)
    if stdin_mode:
        print(svg_string)
    else:
        if output_svg == sys.stdout:
            output_svg.write(svg_string)
        else:
            with open(output_svg, "w") as f:
                f.write(svg_string)
        print(f"%inf:csv_print_timepoint: {output_svg} ws created.", file=sys.stderr)


def do_only_pu_mode(pu_file, output_svg, plantuml_cmd):
    if pu_file == sys.stdin:
        pu_text = "".join(pu_file.readlines())
    else:
        with open(pu_file, "r") as f:
            pu_text = "".join(f.readlines())

    pu_groups_s = re.findall(r"-- <size:\d+><b>[^<]+</b></size> --", pu_text)
    if len(pu_groups_s) == 0:
        pu_groups = []
    else:
        pu_groups = [re.sub(r"-- <size:\d+><b>([^<]+)</b></size> --", r"\1", v) for v in pu_groups_s]

    make_svg(pu_text, output_svg, pu_groups, plantuml_cmd)


if __name__ == "__main__":
    args = init()
    csv_file = args.csv_file
    datetime_column = args.datetime_column

    title = args.TITLE
    group_column = args.GCOLUMN
    tag_column = args.TCOLUMN
    datetime_format = args.DFORMAT

    shrink_mode = args.SHRINK
    only_pu = args.ONLY_PU

    plantuml_cmd = args.PCOMMAND

    # -- check plantuml command
    try:
        ret = subprocess.run([plantuml_cmd, "-h"], capture_output=True)
        if ret.returncode != 0:
            mes = f"??error:csv_print_timepoint: {plantuml_cmd} was not found"
            print(mes, file=sys.stderr)
            sys, exit(1)
    except FileNotFoundError as e:
        mes = f"??error:csv_print_timepoint: {plantuml_cmd} was not found"
        print(mes, file=sys.stderr)
        sys, exit(1)

    stdin_mode = False
    if csv_file == "-":
        csv_file = sys.stdin
        stdin_mode = True
        output_svg = sys.stdout
    else:
        file_prefix = str(Path(csv_file).stem)
        output_pu = file_prefix + ".pu"
        output_svg = file_prefix + ".svg"
        output_tags = file_prefix + "_tags.csv"

    # -- only pu mode
    if only_pu:
        try:
            do_only_pu_mode(csv_file, output_svg, plantuml_cmd)
        except Exception as e:
            print("??error:csv_print_timepoint:", e, file=sys.stderr)
        sys.exit(1)

    if datetime_column is None:
        print("??error:csv_print_timepoint:DATETIME_COLUMN is required.", file=sys.stderr)
        sys.exit(1)

    csv_df = pd.read_csv(csv_file)
    csv_df[datetime_column] = pd.to_datetime(csv_df[datetime_column], format=datetime_format)

    if group_column is not None:
        pu_groups = list(csv_df[group_column])
    else:
        group_column = "group"
        pu_groups = [group_column]
        csv_df[group_column] = " "

    pu_text, pu_tags = make_gantt(csv_df,
                                  datetime_column,
                                  group_column=group_column,
                                  headline_column=tag_column,
                                  title=title,
                                  summarize_by_date=shrink_mode)

    if not stdin_mode:
        with open(output_pu, "w") as f:
            f.write(pu_text)
        with open(output_tags, "w") as f:
            f.write(pu_tags)
        print(f"%inf:csv_print_timepoint: {output_pu} and {output_tags} was created.", file=sys.stderr)

    try:
        make_svg(pu_text, output_svg, pu_groups, plantuml_cmd)
    except Exception as e:
        print("??error:csv_print_timepoint:", e, file=sys.stderr)
        sys.exit(1)
