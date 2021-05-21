#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_print_timeline_trim_svg.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2021 by m.na.akei
# Time-stamp:   <2021-05-19 17:47:04>
# Licence:
# ----------------------------------------------------------------------
import argparse
import fileinput
import textwrap
import sys

from pathlib import Path

import re
from lxml import etree

VERSION = 1.0


def init():
    # argparse --- コマンドラインオプション、引数、サブコマンドのパーサー  Python 3.8.5 ドキュメント https://docs.python.org/ja/3/library/argparse.html
    arg_parser = argparse.ArgumentParser(description="helper tool for csv_print_timeline.sh",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
example:

'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))

    arg_parser.add_argument('TAGS_FILE', metavar='TAGS_FILE', help='path of output from csv_print_html_tl.py', default=None)
    arg_parser.add_argument('PU_FILE', metavar='PU_FILE', help='path of output from csv_print_html_tl.py', default=None)
    arg_parser.add_argument('SVG_FILE', metavar='SVG_FILE', help='path of result that was converted from PU', default=None)
    arg_parser.add_argument('HTML_FILE', metavar='HTML_FILE', help='path of html to make link', default=None)

    args = arg_parser.parse_args()
    return args


def read_tags(tag_file):
    results_dic = {}
    with open(tag_file, "r") as f:
        count = 0
        for line in f.readlines():
            if count == 0:
                count = 1
                continue
            line = line.strip()
            if line.startswith("#") or len(line) == 0:
                continue
            cvs = re.split(r"\s*(?<!\\),\s*", line)
            results_dic[cvs[1]] = cvs[0]
    return results_dic


def read_pu(pu_file):
    results = []
    with open(pu_file, "r") as f:
        count = 0
        for line in f.readlines():
            if count == 0:
                count = 1
                continue
            line = line.strip()
            if line.startswith("#") or len(line) == 0:
                continue
            m = re.match(r"-- <size:18><b>(\S+)</b></size> --", line)
            if m is not None:
                results.append(m.group(1))

    return results


def add_style(svg_root, pu_groups):
    for pg in pu_groups:
        for elm in svg_root.xpath(f"//*/svg:text[contains(text(),'{pg}')]", namespaces=xml_ns):
            elm.set("class", "hover_text")
    #    echo "s/<\/g><\/svg>/<\/g><style type='text\/css'>a:hover {font-weight:bold;font-size:110%;}<\/style><\/svg>/;" >> ${SED_SCR_F}
    style_elm = etree.Element('style')
    style_elm.set("type", "text/css")
    style_elm.text = "a:hover {font-weight:bold;font-size:110%;}"
    svg_root.append(style_elm)


def add_script(svg_root):
    # reactjs - Position sticky SVG element contained inside div with overflow - Stack Overflow https://stackoverflow.com/questions/58401288/position-sticky-svg-element-contained-inside-div-with-overflow
    scr_text = '''
window.addEventListener("scroll",
			function(evt) {

			    var nodes=document.querySelectorAll("text.hover_text")
			    nodes.forEach(
				function(elm){
				    elm.setAttribute("x", screenXtoSVGUnits(window.scrollX) + 10);
				});
			}
		       );

function screenXtoSVGUnits(val) {
    const svg = document.getElementsByTagName("svg")[0];
    let pt = svg.createSVGPoint();
    pt.x = val;
    pt.y = 0;
    pt = pt.matrixTransform(svg.getCTM().inverse());
    return pt.x;
}
'''
    script_elm = etree.Element('script')
    script_elm.set("type", "text/javascript")
    script_elm.text = scr_text
    svg_root.append(script_elm)


if __name__ == "__main__":
    args = init()
    tags_file = args.TAGS_FILE
    pu_file = args.PU_FILE
    svg_file = args.SVG_FILE
    html_file = args.HTML_FILE

    print("%inf:csv_print_timeline_trim_svg:triming svg", file=sys.stderr)

    tags_dic = read_tags(tags_file)
    pu_groups = read_pu(pu_file)

    svg_parser = etree.XMLParser(ns_clean=True, encoding="utf8")
    svg_tree = etree.parse(svg_file, svg_parser)
    svg_root = svg_tree.getroot()
    xml_ns = {"svg": "http://www.w3.org/2000/svg"}

    for k in tags_dic.keys():
        for elm in svg_root.xpath(f"//*/svg:text[contains(text(),'{k}')]", namespaces=xml_ns):
            a_elm = etree.Element('a')
            a_elm.text = k
            rid = "rid_" + tags_dic[k]
            a_elm.set("href", f"{html_file}#{rid}")
            a_elm.set("target", "_blank")
            elm.append(a_elm)
            elm.text = ""

    add_style(svg_root, pu_groups)
    add_script(svg_root)

    svg_string = etree.tostring(svg_root, encoding="utf8", method="xml")
    svg_string = svg_string.decode('utf8')
    print(svg_string)
