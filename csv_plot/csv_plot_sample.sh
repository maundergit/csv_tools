#!/bin/bash
# -*- mode: sh;-*-
#----------------------------------------------------------------------
# Author:       m.akei
# Copyright:    (c)2020 , m.akei
# Time-stamp:   <2020-10-16 16:41:53>
#
#  Copyright (c) 2021 Masaharu N. Akei
#
#  This software is released under the MIT License.
#    http://opensource.org/licenses/mit-license.php
#----------------------------------------------------------------------
DTSTMP=$(date +%Y%m%dT%H%M%S)

DDIR=$(dirname $0)
SNAME=$(basename $0)
#DDIR_ABS=$(cd $(dirname ${DDIR}) && pwd)/$(basename $DDIR)
DDIR_ABS=$(realpath ${DDIR})
TMPDIR=/tmp
# TMPDIR=/tmp/${SNAME}.$$

csv_plot_scatter_matrix.py --columns="ABC001","ABC002","ABC003" --category="ABC004" --format=html test_plot.csv
csv_plot_scatter_3d.py --format=html --category=COL_0006 --size_column=COL_0107 big_sample_arb.csv COL_0008 COL_0033 COL_0097
csv_plot_scatter.py --format=html --category=COL_0006  --size_column=COL_0097 --side_hist=rug big_sample_arb.csv COL_0008 COL_0003
csv_plot_scatter.py --format=html --category=COL_0006  --size_column=COL_0097 --side_hist=box big_sample_arb.csv COL_0008 COL_0003
csv_plot_scatter.py --format=html --category=COL_0006  --size_column=COL_0097 --side_hist=violin big_sample_arb.csv COL_0008 COL_0003
csv_plot_scatter.py --format=html --category=COL_0006  --size_column=COL_0097 --side_hist=histogram big_sample_arb.csv COL_0008 COL_0003
csv_plot_scatter.py --format=html --category=COL_0006  --size_column=COL_0097 --trendline=ols big_sample_arb.csv COL_0008 COL_0003
csv_plot_scatter.py --format=html --category=COL_0006  --size_column=COL_0097 --trendline=lowess big_sample_arb.csv COL_0008 COL_0003

csv_plot_quiver.py --title="sample of quiver chart" --format=html test_quiver.csv X Y U V

csv_plot_heatmap.py --xrange=0,.5 --yrange=0,.5 --format=html test_plot.csv ABC001 ABC002
csv_plot_heatmap.py --xrange=0,.5 --yrange=0,.5 --side_hist=box --format=html test_plot.csv ABC001 ABC002
csv_plot_heatmap.py --xrange=0,.5 --yrange=0,.5 --side_hist=rug --format=html test_plot.csv ABC001 ABC002
csv_plot_heatmap.py --xrange=0,.5 --yrange=0,.5 --side_hist=violin --format=html test_plot.csv ABC001 ABC002
csv_plot_heatmap.py --xrange=0,.5 --yrange=0,.5 --side_hist=histogram --format=html test_plot.csv ABC001 ABC002
csv_plot_heatmap.py --xrange=0,.5 --yrange=0,.5 --side_hist=histogram --contour --format=html test_plot.csv ABC001 ABC002
csv_plot_heatmap.py --xrange=0,.5 --yrange=0,.5 --side_hist=histogram --hist_func="count" --format=html test_plot.csv ABC001 ABC002
csv_plot_heatmap.py --xrange=0,.5 --yrange=0,.5 --side_hist=histogram --hist_func="avg" --format=html test_plot.csv ABC001 ABC002
csv_plot_heatmap.py --xrange=0,.5 --yrange=0,.5 --side_hist=histogram --hist_func="min" --format=html test_plot.csv ABC001 ABC002
csv_plot_heatmap.py --xrange=0,.5 --yrange=0,.5 --side_hist=histogram --hist_func="max" --format=html test_plot.csv ABC001 ABC002

csv_plot_strip.py --facets=day --category=sex --format=html test_strip.csv total_bill time
csv_plot_strip.py --facets=day --category=sex --format=html --mode=overlay test_strip.csv total_bill time

csv_plot_polar.py --format=html --type=line --category=strength --line_close --line_shape=spline --start_angle=90 --direction="clockwise" test_polar.csv frequency direction frequency
csv_plot_polar.py --format=html --type=bar --category=strength --start_angle=90 --direction="clockwise" test_polar.csv frequency direction frequency
csv_plot_polar.py --format=html --type=scatter --category=strength --start_angle=90 --direction="clockwise" test_polar.csv frequency direction frequency

csv_plot_box.py --category=sex --format=html --type=violin test_strip.csv total_bill time
csv_plot_box.py --category=sex --format=html --type=box test_strip.csv total_bill time

csv_plot_bar.py --format=html --category=medal --barmode=group test_bar.csv nation count
csv_plot_bar.py --format=html --category=medal --barmode=overlay test_bar.csv nation count
csv_plot_bar.py --format=html --category=medal --barmode=relative test_bar.csv nation count

csv_plot_line_3d.py --format=html --category=COL_0006 big_sample_arb.csv COL_0008 COL_0033 COL_0097
csv_plot_line.py --facets=COL_0006 --format html big_sample_arb.csv COL_0000 COL_0008,COL_0033,COL_0097
csv_plot_histogram.py --nbins=50  --category="ABC004" --side_hist=rug --log_y --format=html test_plot.csv  "ABC001" "ABC002"
csv_plot_histogram.py --nbins=50  --category="ABC004" --hist_func=sum --log_y --format=html test_plot.csv  "ABC001" "ABC002"
csv_plot_histogram.py --nbins=50  --category="ABC004" --hist_func=avg --log_y --format=html test_plot.csv  "ABC001" "ABC002"
csv_plot_histogram.py --nbins=50  --category="ABC004" --hist_func=min --log_y --format=html test_plot.csv  "ABC001" "ABC002"
csv_plot_histogram.py --nbins=50  --category="ABC004" --hist_func=max --log_y --format=html  test_plot.csv  "ABC001" "ABC002"
csv_plot_histogram.py --nbins=50  --category="ABC004" --side_hist=box --log_y --output=test_plot_histogram_side_box.html  test_plot.csv  "ABC001" "ABC002"
csv_plot_parallel_coordinates.py --format=html --discrete big_sample_arb.csv COL_0008 COL_0006,COL_0002,COL_0023

csv_plot_parallel_coordinates.py --format=html --discrete big_sample_arb.csv COL_0008 COL_0006,COL_0002,COL_0023
csv_plot_parallel_coordinates.py --ignore_key --output=big_sample_arb_parallel_ignore_key.html --discrete big_sample_arb.csv COL_0008 COL_0006,COL_0002,COL_0023

csv_plot_annotated_heatmap.py --format=html --x=B,C,D,E --y=A --show_scale --x_title=XAXIS --y_title=YAXIS test_annotated_heatmap.csv

csv_uty.py --change_timefreq='D=ABC002:%Y-%m-%d %H\:%M\:%S:floor:10s' bit-pattern-headers.csv|\
     csv_status.py --mode sum --group D -|csv_uty.py --drop_columns=ABC000,ABC001 - |\
     csv_uty.py --stack=D - |csv_plot_bar.py --output=bit-pattern-headers_10sec_sum.html --animation_column=D --yrange=0,5 - category stacked_result


make_iframes_rowcol.sh -t {b,t}*.html > subplot.html

#----
# remove_tmpdir
#-------------
# Local Variables:
# mode: sh
# coding: utf-8-unix
# End:

