#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_print_html_tl.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2021 by m.na.akei
# Time-stamp:   <2021-04-30 11:39:17>
# Licence:
# ----------------------------------------------------------------------
import argparse
import textwrap
import sys

from pathlib import Path

import re
import html
import json

import calendar

import datetime
from pathlib import Path
# import xml.etree.ElementTree as ET
from lxml import etree

import numpy as np
import pandas as pd
import minify_html

PIL_PKG = True
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
except Exception as e:
    PIL_PKG = False

sys.path.insert(0, format(Path(__file__).parent))
from csv_print_html_oia import part_color

VERSION = 1.0


def init():
    arg_parser = argparse.ArgumentParser(description="print html table made of csv with estimation",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
remark:

  Generated html uses script of TimelineJS3. if you used CDN(cdn.knightlab.com), use '--cdn'.
  Without '--cdn', those scripts must be gotten from 'cdn.knightlab.com' and 
  those scripts must be stored in 'timeline3' directory in the same directory as html.
  see "Loading Files Locally" section in Timeline https://timeline.knightlab.com/docs/instantiate-a-timeline.html .

  For '--part_color', is you want to use comma(,) an colon(:) in word, then those must be escaped by "\".
  Using '--group_by_part_color', words in '--part_color' are used as group of event/milestone in tileline/gantt chart.
  when '--part_color' is used, also gantt chart for plantUML will be created. 
  then value of column('--headingline_column') will be used as name of milestone.

  about '--media':
  TimelineJS3 has function to show media(image,vide,etc) for each event.
  using '--media' option, this function is enable: 
  path of media file is given by this option. optional column is column that has title string of each media file.

  '--words_map' was path of map file to replace words to group on timeline.
  format of the file is following: 'group: word[,word..]' at each row.

  about '--module_figure', see https://github.com/maundergit/csv_tools/blob/master/TextTimeseries2.md.

  aboutn TimelineJS3 see following:
  GitHub - NUKnightLab/TimelineJS3: TimelineJS v3: A Storytelling Timeline built in JavaScript. http://timeline.knightlab.com https://github.com/NUKnightLab/TimelineJS3

example:
  cat test3.csv
IDX,B,DT,C,O,I,A,image,title_of_image
1,A,2021-06-01 10:00:00,Sample1,Observation1:this is a pen,Investigation1:Atre you there?,Action1: nothing to do,pattern.png,sample
2,B,2021-07-01 10:00:00,Sample2,Observation2:this is a pen,Investigation2:Atre you there?,Action2: nothing to do,pattern.png,sample
3,C,2021-08-01 10:00:00,Sample3,Observation3:this is a pen,Investigation2:Atre you there?,Action3: nothing to do,pattern.png,sample

  csv_print_html_tl.py --columns=IDX,B,C --part_color='pen:red,action2:blue,observation3:black' --output=test.html test3.csv DT O I A
  csv_print_html_tl.py --columns=IDX,B,C --part_color='pen:red,action2:blue,observation3:black' --output=test.html --group_column=B test3.csv DT O I A
  csv_print_html_tl.py --columns=IDX,B,C --part_color='pen:red,action2:blue,observation3:black'\
 --output=test.html --group_column=B --headline_column=B test3.csv DT O I A
  csv_print_html_tl.py --columns=IDX,B,C --part_color='pen:red,action2:blue,observation3:black'\
 --output=test.html --group_column=B --headline_column=B --title="Title\ndescription" test3.csv DT O I A
  csv_print_html_tl.py --columns=IDX,B,C --part_color='pen:red,action2:blue,observation3:black'\
 --output=test.html --group_by_part_color --headline_column=B --title="Title\\ndescription" test3.csv DT O I A
  csv_print_html_tl.py --columns=IDX,B,C --part_color='pen:red,action2:blue,observation3:black'\
 --output=test.html --group_by_part_color --headline_column=B --media=image:title_of_image --title="Title\ndescription" test3.csv DT O I A

  csv_print_html_tl.py --datetime_format='%Y-%m-%d' --columns=date --part_color='吾輩,人間,我慢,書斎'\
 --group_by_part_color --output=test.html --module_figure=wagahaiwa_nekodearu.svg wagahaiwa_nekodearu.csv date content
  csv_print_html_tl.py --datetime_format='%Y-%m-%d' --columns=date --part_color='吾輩,人間,我慢,書斎'\
 --group_by_part_color --output wagahaiwa_nekodearu_2.html --module_figure "wagahaiwa_nekodearu_module.svg:7" --words_map=wagahaiwa_nekodearu_map.txt  wagahaiwa_nekodearu.csv date content



'''))
    #  --part_color='インドネシア:red,米国:green,潜"水艦:blue,海軍\S*参謀総?長:black'

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))

    arg_parser.add_argument("--title", dest="TITLE", help="title and description", type=str, metavar='TITLE', default=None)

    arg_parser.add_argument("--datetime_format",
                            dest="DTFORMAT",
                            help="format string for column of datetime,default=%%Y-%%m-%%d %%H:%%M:%%S",
                            type=str,
                            metavar="FORMAT",
                            default="%Y-%m-%d %H:%M:%S")

    arg_parser.add_argument("--headline_column",
                            dest="HCOLUMN",
                            help="names of column for short text as name of event/milestone",
                            type=str,
                            metavar='COLUMN',
                            default=None)

    arg_parser.add_argument("--columns",
                            dest="COLUMNS",
                            help="names of addtional columns",
                            type=str,
                            metavar='COLUMNS[,COLUMNS...]',
                            default=None)

    arg_parser.add_argument("--part_color",
                            dest="PCOLORS",
                            help="part color for string, color code is one in css codes.",
                            type=str,
                            metavar='STRING:COLOR[,STRING:COLOR...]',
                            default=None)

    arg_parser.add_argument("--group_column",
                            dest="GCOLUMN",
                            help="names of column to make group",
                            type=str,
                            metavar='COLUMN',
                            default=None)
    arg_parser.add_argument("--group_by_part_color",
                            dest="GSEARCH",
                            help="grouping by result of part_color",
                            action="store_true",
                            default=False)

    arg_parser.add_argument("--media", dest="MEDIA", help="columns for medias", type=str, metavar="COLUMN[:COLUMN]", default=None)
    arg_parser.add_argument("--module_figure",
                            dest="MFIGURE",
                            help="path of module figure, period, map file. if defined, '--media' is ignored.",
                            type=str,
                            metavar="SVG_FILE[:INT]",
                            default=None)

    arg_parser.add_argument("--words_map",
                            dest="WMAP",
                            help="path of file to replace group on timeline",
                            type=str,
                            metavar='COLUMN',
                            default=None)

    arg_parser.add_argument("--cdn", dest="CDN", help="using CDN(cdn.knightlab.com), default=local", action="store_true", default=False)

    arg_parser.add_argument("--output_file", dest="OUTPUT", help="path of output file", type=str, metavar='FILE', default=None)
    arg_parser.add_argument("--minify", dest="MINIFY", help="minifing html", action="store_true", default=False)

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='file to read, if empty, stdin is used')

    arg_parser.add_argument('datetime_column', metavar='COLUMN_OF_DATETIME', help="name of column of datetime")

    arg_parser.add_argument('oia_columns', metavar='COLUMN', nargs="+", help="colum names of Observation/Investigation/Action")

    args = arg_parser.parse_args()
    return args


def make_json(df,
              datetime_column,
              columns,
              oia_columns,
              pcolors,
              group_column=None,
              headline_column=None,
              title=None,
              group_by_part_color=False,
              media_column=None,
              media_caption=None,
              module_figure_file=None,
              module_figure_time_window=None,
              words_map_file=None):

    j_data = {}
    if title is not None:
        cvs = re.split(r"\\n", title)
        if len(cvs) > 1 and len(cvs[1].rstrip()) > 0:
            title_0 = cvs[0]
            title_1 = cvs[1]
        else:
            title_0 = cvs[0]
            title_1 = ""
        j_data["title"] = {"text": {"headline": title_0, "text": title_1}}

    module_figure = None
    module_figure_output_dir = "fig"
    if module_figure_file is not None:
        module_figure = module_state_figure(module_figure_file,
                                            module_figure_output_dir,
                                            map_file=words_map_file,
                                            duration=module_figure_time_window)
    words_map_n2w = None
    words_map_w2n = None
    if words_map_file is not None:
        words_map_n2w, words_map_w2n = read_words_map_file(words_map_file)

    events = []
    output_df = pd.DataFrame()
    for ir, row in df.iterrows():
        dt_c = row[datetime_column]
        if dt_c is pd.NaT:
            continue
        evn = make_event(row,
                         dt_c,
                         columns,
                         oia_columns,
                         pcolors,
                         group_column=group_column,
                         headline_column=headline_column,
                         group_by_part_color=group_by_part_color,
                         media_column=media_column,
                         media_caption=media_caption,
                         module_figure=module_figure,
                         words_map=words_map_w2n)

        events.append(evn)
        output_df = output_df.append(row, ignore_index=True)
    j_data["events"] = events

    j_str = json.dumps(j_data)
    return j_str, output_df


def get_title_from_exif(image_file):
    im = Image.open(image_file)
    exif_dic = im.getexif()
    exif_tbl = {}
    for tag_id, value in exif_dic.items():
        tag_name = TAGS.get(tag_id, tag_id)
        exif_tbl[tag_name] = value

    chk = [v for v in exif_tbl.keys() if v.lower() == "title"]
    if len(chk) > 0:
        return exif_tbl[chk[0]]
    chk = [v for v in exif_tbl.keys() if v.lower() == "comment"]
    if len(chk) > 0:
        return exif_tbl[chk[0]]
    return None


def __make_group(group, words_map_n2w):
    if words_map_n2w is None:
        return group
    result = set()
    cvs = re.split(r"\s*(?<!\\),\s*", group)
    for v in cvs:
        if v in words_map_n2w:
            v = words_map_n2w[v]
            result |= set(v)
        else:
            result.add(v)
    result = sorted(list(result))

    return ",".join(result)


def make_event(row,
               dt_c,
               columns,
               oia_columns,
               pcolors,
               group_column=None,
               headline_column=None,
               group_by_part_color=False,
               media_column=None,
               media_caption=None,
               module_figure=None,
               words_map=None):
    evnt = {}
    evnt["start_date"] = {
        "year": str(dt_c.year),
        "month": str(dt_c.month),
        "day": str(dt_c.day),
        "hour": str(dt_c.hour),
        "minute": str(dt_c.minute)
    }
    evnt["display_date"] = dt_c.strftime("%Y-%m-%d %H:%M:%S")
    evnt_desc, hit_words_dic = make_table(row, columns, oia_columns, pcolors)
    if headline_column is not None:
        headline = row[headline_column]
    else:
        headline = f"Event{dt_c}"
    evnt["text"] = {"headline": headline, "text": evnt_desc}
    if group_by_part_color:
        hit_words = sorted(list(set(hit_words_dic.keys())))
        evnt["group"] = ",".join(hit_words) if len(hit_words) > 0 else ""
        evnt["group"] = __make_group(evnt["group"], words_map)
        row["group"] = evnt["group"]
    elif group_column is not None:
        row[group_column] = __make_group(row[group_column], words_map)
        evnt["group"] = row[group_column]

    if module_figure is not None:
        module_figure.edit_module_figure(hit_words_dic.keys(), dt_c)
        tag = dt_c.strftime("%Y-%m-%dT%H%M%S")
        media_file = module_figure.write(tag)
        media_title = Path(media_file).stem
        evnt["media"] = {"url": f"{media_file}", "caption": media_title, "title": media_title}
    elif media_column is not None:
        media_file = row[media_column]
        if media_file is not np.nan and len(media_file) > 0:
            if media_caption is not None and row[media_caption] is not np.nan and len(row[media_caption]) > 0:
                media_title_s = row[media_caption]
            else:
                if PIL_PKG:
                    exif_title = get_title_from_exif(media_file)
                    if exif_title is not None and len(exif_title) > 0:
                        media_title_s = exif_title
                    else:
                        media_title_s = media_file
                else:
                    media_title_s = media_file
            evnt["media"] = {"url": f"{media_file}", "caption": media_title_s, "title": media_title_s}
    return evnt


def make_table(row, columns, oia_columns, pcolors):
    html_str = '<table class="desc_oia">\n'
    html_str += '<thead>\n'
    html_str += f'<th nowrap="1"">項目</th><th>内容</th>\n'
    html_str += '</thead>\n<tbody>\n'

    hit_words = {}
    for c in columns:
        v = html.escape(str(row[c]))
        if pcolors is not None and len(pcolors) > 0:
            v, hw = part_color(pcolors, v)
            hit_words.update(hw)
        v = "&nbsp;" if v == "" else v
        html_str += f'<tr><td nowrap="1">{c}</td><td>{v}</td></tr>\n'
    for ic, c in enumerate(oia_columns):
        v0 = str(row[c])
        v = html.escape(str(v0))
        if pcolors is not None and len(pcolors) > 0:
            v, hw = part_color(pcolors, v)
            hit_words.update(hw)
        v = "&nbsp;" if v == "" else v
        html_str += f'<tr><td nowrap="1">{c}</td><td>{v}</td></tr>\n'
    html_str += "</tbody>\n</table>\n"

    return html_str, hit_words


def make_html(json_str, word_colors, timeline_local=True):
    word_colors = re.sub(r"\"", "&quot;", word_colors)
    json_str = re.sub(r"\\", "\\\\\\\\", json_str)
    if timeline_local:
        timeline_pkg = '''
    <link title="timeline-styles" rel="stylesheet" href="timeline3/css/timeline.css" />
    <script src="timeline3/js/timeline-min.js"></script>
'''
    else:
        timeline_pkg = '''
    <link title="timeline-styles" rel="stylesheet" 
          href="https://cdn.knightlab.com/libs/timeline3/latest/css/timeline.css" />
    <script src="https://cdn.knightlab.com/libs/timeline3/latest/js/timeline.js"></script>
'''
    text = f'''
<?xml version="1.0" encoding="utf-8"?>
<html>
  <head>
  <!-- made by csv_print_html_tl.py -->
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Cache-Control" content="no-store">
    <meta http-equiv="Expires" content="0">
{timeline_pkg}
    <style type="text/css">
      span.word_view_span {{
        font-weight:bold;
        background:#EEEEEE;
        box-shadow: 0.0625em 0.0625em 0.0625em 0.0625em rgba(0,0,0,0.4);
        border-radius: 0.25em;
        padding-left:0.2em;
        padding-right:0.2em;
	margin-right:0.2em;
      }}
      table.desc_oia {{ 
         box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
      }}
      table.desc_oia caption {{
         font-weight: bold;
      }}
      table.desc_oia th {{
         background-color: #009879;
	 padding:6px;
      }}
      table.desc_oia thead tr th {{
         border-bottom: solid 1px;
         color: #ffffff;
      }}
      table.desc_oia td {{
         padding:6pt; 
      }}
      table.desc_oia tbody tr {{
         border-bottom: 1px solid #dddddd;
         background-color: #ffffff;
      }}
      table.desc_oia tbody td {{
         border-bottom: 1px solid #dddddd;
         background-color: #ffffff;
      }}
    </style>
  </head>
  <body>
    <div id='timeline-embed' style="width: 100%;">
    </div>
    <script type="text/javascript">
      var tl_opts={{
      "width":"80vw",
      "is_embed":false,
      "scale_factor":2,
      "initial_zoom":2,
      "zoom_sequence":[0.02,0.04,0.1,0.2,0.5,1, 2, 3, 5, 8, 13, 21, 34, 55, 89],
      "timenav_position":"top",
      "start_at_slide":0,
      }}
      var json_data=JSON.parse('{json_str}');
      timeline = new TL.Timeline('timeline-embed', json_data, tl_opts);
    </script>
   <input value="{word_colors}" style="display:none" />
  </body>
</html>

'''
    return text


#      "timenav_height":250,


def make_gantt(df, datetime_column, group_column="group", headline_column=None, title=None):
    separator_font_size = 18
    groups = sorted(list(df[group_column].unique()))

    if headline_column is not None:
        df[headline_column] = df[headline_column].apply(lambda x: re.sub(r"\n", "", x))
        vc = df[headline_column].value_counts()
        hc_id_names = set(list(vc.loc[vc > 1].index))  # headline_columnで指定されるカラムで二個以上ある値のリスト

    id_names = []
    dt_0 = df[datetime_column].min()
    dt_1 = df[datetime_column].max()
    dt_1 = dt_1.replace(day=calendar.monthrange(dt_1.year, dt_1.month)[1])  # 月末日付の入手

    result_s = ["@startgantt", f"Project starts {dt_0.year}-{dt_0.month}-01"]
    if title is not None:
        result_s.append(f"title {title}")
    # 表示で幅を持たすためのダミータスク
    result_s.append(f"[ ] starts {dt_0.year}-{dt_0.month}-01 and ends {dt_1.year}-{dt_1.month}-{dt_1.day}")
    result_s.append("printscale weekly")
    for grp in groups:
        if len(grp) == 0:
            continue
        result_s.append(f"-- <size:{separator_font_size}><b>{grp}</b></size> --")
        ds = df.loc[df[group_column] == grp, datetime_column]
        for idx, dt in ds.items():
            dt_s = dt.strftime("%Y-%m-%d")
            if headline_column is not None:  # headline_columnでタスク名生成が指定されている場合
                id_name = df.loc[df.index == idx, headline_column].iat[0]
                idn = len([v for v in id_names if v == id_name])
                id_names.append(id_name)
                if idn > 0:  # 既にタスク名として資料済みの場合は連番付与
                    id_name = f"{id_name}_{idn}"
                elif id_name in hc_id_names:  # 二個以上あるタスク名は連番として0を付与
                    id_name = f"{id_name}_0"
            else:
                id_name = f"id_{idx}"
            result_s.append(f"[{id_name}] happens {dt_s}")

    result_s.append("@endgantt")
    result = "\n".join(result_s)
    return result


def read_words_map_file(map_file):
    words_map_n2w = {}
    words_map_w2n = {}
    if not Path(map_file).exists():
        mes = f"??error:csv_print_html_tl:{map_file} was not found"
        print(mes, file=sys.stderr)
        raise Exception(mes)
    print(f"%inf:csv_print_html_tl:words_map '{map_file}' is used.", file=sys.stderr)
    with open(map_file, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith("#") or len(line) == 0:
                continue
            cvs = re.split(r"\s*(?<!\\):\s*", line, maxsplit=2)
            if len(cvs) < 2:
                mes = f"??error:module_state_figure:invalid structure in map file: {map_file}:{line}"
                print(mes, sys.stderr)
                raise Exception(mes)
            words_map_n2w[cvs[0]] = cvs[1]

    for k, v in words_map_n2w.items():
        cvs = re.split(r"\s*(?<!\\),\s*", v)
        for v2 in cvs:
            if v2 not in words_map_w2n:
                words_map_w2n[v2] = []
            words_map_w2n[v2] = sorted(list(set(words_map_w2n[v2]) | set([k])))

    # print(words_map_w2n)
    print(f"%inf:csv_print_html_tl:words_map:\n{words_map_w2n}", file=sys.stderr)
    return words_map_n2w, words_map_w2n


class module_state_figure():
    def __init__(self, svg_file, output_dir, duration=3600 * 24 * 14, datetime_format="%Y-%m-%d %H:%M:%S", map_file=None):
        self.__svg_file = svg_file
        self.__output_dir = output_dir
        self.__svg_root = self.read_module_figure()
        self.__duration = duration
        self.__datetime_format = datetime_format
        self.__name2words = {}
        self.__words2names = {}
        if map_file is not None:
            self.read_map_file(map_file)

        self.__stroke_width = 0.25

    def read_module_figure(self):
        if not Path(self.__svg_file).exists():
            mes = f"??error:module_state_figure:{self.__svg_file} was not found"
            print(mes, file=sys.stderr)
            raise Exception(mes)
        self.__tree = etree.parse(self.__svg_file)
        svg_root = self.__tree.getroot()

        return svg_root

    def read_map_file(self, map_file):
        if not Path(map_file).exists():
            mes = f"??error:module_state_figure:{map_file} was not found"
            print(mes, file=sys.stderr)
            raise Exception(mes)
        with open(map_file, "r") as f:
            for line in f.readlines():
                line = line.strip()
                if line.startswith("#") or len(line) == 0:
                    continue
                cvs = re.split(r"\s*(?<!\\):\s*", line, maxsplit=2)
                if len(cvs) < 2:
                    mes = f"??error:module_state_figure:invalid structure in map file: {map_file}:{line}"
                    print(mes, sys.stderr)
                    raise Exception(mes)
                self.__name2words[cvs[0]] = cvs[1]

        for k, v in self.__name2words.items():
            cvs = re.split(r"\s*(?<!\\),\s*", v)
            for v2 in cvs:
                if v2 not in self.__words2names:
                    self.__words2names[v2] = []
                # self.__words2names[v2].append(k)
                self.__words2names[v2] = sorted(list(set(self.__words2names[v2]) | set([k])))

        # print(self.__words2names)

    def edit_module_figure(self, id_names0, current_dt):

        if len(self.__words2names) > 0:
            id_names = []
            for id_name in id_names0:
                if id_name in self.__words2names:
                    id_names.extend(self.__words2names[id_name])
                    id_names.append(id_name)
                else:
                    id_names.append(id_name)
        else:
            id_names = id_names0

        self.set_opacity0_in_svg(current_dt)
        for id_name in id_names:
            self.set_opacity1_in_svg(id_name, current_dt)
        svg_string = self.get_string()

        return svg_string

    def __get_style(self, elm):
        e_style = elm.get("style")
        if e_style is None:
            return {}
        e_style_dic = {
            re.split(r"(?<!\\):", v, maxsplit=2)[0]: re.split(r"(?<!\\):", v, maxsplit=2)[1]
            for v in re.split(r"\s*(?<!\\);\s*", e_style) if len(v) > 0
        }
        return e_style_dic

    def __set_opacity(self, elm, o_code, w_code, current_dt, force=False):
        e_style_dic = self.__get_style(elm)

        if ("fill-opacity" in e_style_dic and float(e_style_dic["fill-opacity"]) <= 0.0) and not force:
            return
        e_style_dic["fill-opacity"] = f"{o_code}"
        e_style_dic["stroke-width"] = f"{w_code}"
        e_style = ";".join([f"{k}:{v}" for k, v in e_style_dic.items()])
        elm.set("style", e_style)
        if force:
            elm.set("time_stamp", current_dt.strftime(self.__datetime_format))

    def __calculate_stroke_width(self, dt, s_width, duration, reverse=False):
        if reverse:
            # w_code_f = max(1.0, 1 - duration / dt) / 2 * s_width if dt < duration else s_width
            w_code_f = max(self.__stroke_width, s_width - dt / duration *
                           (s_width - self.__stroke_width)) if dt < duration else self.__stroke_width
            # print(s_width, w_code_f, dt, duration)
        else:
            # w_code_f = min(10.0, 1 + duration / dt) / 2 * s_width if dt < duration else s_width
            w_code_f = min(self.__stroke_width * 40, s_width +
                           duration / dt * self.__stroke_width) if dt < duration else self.__stroke_width
        w_code_f = min(40 * self.__stroke_width, w_code_f)
        return w_code_f

    def __calculate_opacity(self, dt, duration):
        c_code_f = 1.0 - dt / duration if dt < duration else 0.0
        return c_code_f

    def set_opacity0_in_svg(self, current_dt):
        default_width = self.__stroke_width
        xml_ns = {"svg": "http://www.w3.org/2000/svg"}
        for elm in self.__svg_root.xpath(f"//*/svg:rect", namespaces=xml_ns):
            tstmp = elm.get("time_stamp")
            if tstmp is None:
                o_code = "0.0"
                w_code = str(default_width)
            else:
                dt = (current_dt - datetime.datetime.strptime(tstmp, self.__datetime_format)).total_seconds()
                f_v = self.__calculate_opacity(dt, self.__duration)
                # print(current_dt, tstmp, dt, f_v)
                o_code = "{:0.6f}".format(f_v)
                # print(elm.get("id"), o_code, dt, self.__duration)
                e_style = self.__get_style(elm)
                w_code_f = float(e_style["stroke-width"])
                if w_code_f > default_width:
                    w_code = str(min(w_code_f, self.__calculate_stroke_width(dt, w_code_f, self.__duration, reverse=True)))
                else:
                    w_code = default_width
            self.__set_opacity(elm, o_code, w_code, current_dt)

    def set_opacity1_in_svg(self, id_name, current_dt):
        # xmlstarlet el  ltest.svg
        # xmlstarlet ed --update '//*/svg:rect[@id="rect1"]/@style' -v 'fill:#00ff00;stroke:#000000;stroke-width:0.264583;fill-opacity:1' test.svg
        default_width = self.__stroke_width
        xml_ns = {"svg": "http://www.w3.org/2000/svg"}
        for elm in self.__svg_root.xpath(f"//*/svg:tspan[contains(text(),'{id_name}')]/ancestor::svg:g/svg:rect", namespaces=xml_ns):
            o_code = "1"
            tstmp = elm.get("time_stamp")
            # print("1:", elm.get('id'))
            if tstmp is not None:
                e_style = self.__get_style(elm)
                w_code_f = float(e_style["stroke-width"])
                dt = (current_dt - datetime.datetime.strptime(tstmp, self.__datetime_format)).total_seconds()
                # print(id_name, elm.get('id'), current_dt, tstmp, dt)
                if dt != 0:
                    w_code = str(self.__calculate_stroke_width(dt, w_code_f, self.__duration))
                else:
                    w_code = f"{w_code_f}"
            else:
                w_code = default_width
            self.__set_opacity(elm, o_code, w_code, current_dt, force=True)

    def get_string(self):
        svg_string = etree.tostring(self.__svg_root, encoding="utf8", method="xml")
        svg_string = svg_string.decode('utf8')
        return svg_string

    def write(self, tag_of_file):
        if not Path(self.__output_dir).exists():
            Path(self.__output_dir).mkdir(exist_ok=True, parents=True)
        fname = Path.joinpath(Path(self.__output_dir), Path(self.__svg_file).stem + f"_{tag_of_file}.svg")
        with open(fname, "w") as f:
            print(self.get_string(), file=f)

        return fname


# svg_file = "test.svg"
# output_dir = "fig"
# id_names = ["吾輩"]
# current_dt = datetime.datetime.now()

# module_figure = module_state_figure(svg_file, output_dir)
# svg_string = module_figure.edit_module_figure(id_names, current_dt)
# current_dt = datetime.datetime.strptime("2021-05-12 10:00:00", "%Y-%m-%d %H:%M:%S")
# svg_string = module_figure.edit_module_figure(id_names, current_dt)
# fname = module_figure.write("11")

if __name__ == "__main__":
    args = init()
    csv_file = args.csv_file
    title = args.TITLE
    output_file_html = args.OUTPUT
    datetime_format = args.DTFORMAT
    datetime_column = args.datetime_column
    oia_columns = args.oia_columns

    timeline_local = not args.CDN

    group_column = args.GCOLUMN
    headline_column = args.HCOLUMN
    columns_s = args.COLUMNS

    media_inf = args.MEDIA
    media_file_column = None
    media_caption_column = None
    if media_inf is not None:
        cvs = re.split(r"\s*(?<!\\):\s*", media_inf)
        if len(cvs) > 2:
            print(f"??error:csv_print_html_tl:invalid media option:{media_inf}", file=sys.stderr)
            sys.exit(1)
        elif len(cvs) > 1:
            media_file_column = cvs[0]
            media_caption_column = cvs[1]
        else:
            media_file_column = cvs[0]
            media_caption_column = media_file_column

    module_figure_s = args.MFIGURE
    module_figure_file = None
    module_figure_time_window = 14 * 3600 * 24
    if module_figure_s is not None:
        cvs = re.split(r":", module_figure_s)
        module_figure_file = cvs[0]
        if len(cvs) >= 2 and cvs[1].isdigit():
            module_figure_time_window = int(cvs[1]) * 3600 * 24
        elif len(cvs) > 2 and not cvs[1].isdigit():
            print(f"??error:csv_print_html_tl:invalid format of '--module_figure': {module_figure_s}", file=sys.stderr)
            sys.exit(1)

    pcolors_s = args.PCOLORS
    group_by_part_color = args.GSEARCH
    if group_by_part_color and pcolors_s is None:
        print("??error:csv_print_html_tl:'--group_by_part_color must be used with '--part_color'.", file=sys.stderr)
        sys.exit(1)
    if group_by_part_color and group_column is not None:
        print(
            "#warn:csv_print_html_tl:both '--group_by_part_color' and '--group_columns' was defined,\n\t but '--group_columns' are ignored",
            file=sys.stderr)

    html_minify = args.MINIFY

    words_map_file = args.WMAP

    if output_file_html is None and csv_file == "-":
        print("??error:csv_print_html_tl:path of output html must e defined.", file=sys.stderr)
        sys.exit(1)

    output_file_gantt = None
    if output_file_html is None:
        output_file_html = str(Path(csv_file).stem) + "_tl.html"
    if output_file_gantt is None:
        output_file_gantt = str(Path(output_file_html).stem) + ".pu"

    output_file_csv = str(Path(output_file_html).stem) + ".csv"

    pcolors = None
    if pcolors_s is not None:
        pcolors = re.split(r"\s*(?<!\\),\s*", pcolors_s)
        print(f"%inf:csv_print_html:part colors: {pcolors}", file=sys.stderr)
    else:
        pcolors_s = ""

    columns = []
    if columns_s is not None:
        columns = re.split(r"\s*,\s*", columns_s)

    if csv_file == "-":
        csv_file = sys.stdin

    output_file_html_f = open(output_file_html, "w")

    csv_df = pd.read_csv(csv_file, dtype='object')
    csv_df[datetime_column] = pd.to_datetime(csv_df[datetime_column], format=datetime_format)
    csv_df.sort_values(datetime_column, inplace=True)
    csv_df.reset_index(inplace=True)

    json_str, output_df = make_json(csv_df,
                                    datetime_column,
                                    columns,
                                    oia_columns,
                                    pcolors,
                                    group_column=group_column,
                                    headline_column=headline_column,
                                    title=title,
                                    group_by_part_color=group_by_part_color,
                                    media_column=media_file_column,
                                    media_caption=media_caption_column,
                                    module_figure_file=module_figure_file,
                                    module_figure_time_window=module_figure_time_window,
                                    words_map_file=words_map_file)
    html_str = make_html(json_str, pcolors_s, timeline_local=timeline_local)

    if html_minify:
        try:
            html_str = minify_html.minify(html_str, minify_js=True, minify_css=True)
        except SyntaxError as e:
            mes = f'??error:csv_print_html_oia:{e}'
            print(mes, file=sys.stderr)
            sys.exit(1)

    print(html_str, file=output_file_html_f)

    print(f"%inf:csv_print_html_tl:{output_file_html} was created.", file=sys.stderr)

    if pcolors is not None:
        gantt_str = make_gantt(output_df, datetime_column, headline_column=headline_column, title=title)
        with open(output_file_gantt, "w") as f:
            f.write(gantt_str)
        print(f"%inf:csv_print_html_tl:{output_file_gantt} was created.", file=sys.stderr)

    output_df.to_csv(output_file_csv)
    print(f"%inf:csv_print_html_tl:{output_file_csv} was created.", file=sys.stderr)
