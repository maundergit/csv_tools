## csv_plot_annotated_heatmap.py
<pre>
usage: csv_plot_annotated_heatmap.py [-h] [-v] [--title TEXT] [--x_title TEXT]
                                     [--y_title TEXT]
                                     [--color_table {1,2,3,4,5,6,7,8,9,10,11,12}]
                                     [--x COLUMN[,COLUMN...]] [--y COLUMN]
                                     [--zrange ZMIN,ZMAX] [--log_z]
                                     [--query QUERY] [--output FILE]
                                     [--format {svg,png,jpg,json,html}]
                                     [--packed_html] [--width WIDTH]
                                     [--height HEIGHT] [--show_scale]
                                     CSV_FILE

create heatmap chart for x-y matrix data

positional arguments:
  CSV_FILE              csv files to read

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --title TEXT          title of chart
  --x_title TEXT        title of x axis
  --y_title TEXT        title of y axis
  --color_table {1,2,3,4,5,6,7,8,9,10,11,12}
                        color table for heat map, default=1
  --x COLUMN[,COLUMN...]
                        names of columns for x
  --y COLUMN            name of column for Y
  --zrange ZMIN,ZMAX    range of Z, this is used for only color scale.
  --log_z               log-scaled Z axis
  --query QUERY         query string to select rows
  --output FILE         path of output file
  --format {svg,png,jpg,json,html}
                        format of output, default=svg
  --packed_html         whether plotly.js is included in result html file,
                        this is enable only for --format=html
  --width WIDTH         width of output
  --height HEIGHT       height of output
  --show_scale          show scale

remark:
  The input data must have the csv format, you may select numerical columns as X and optionaly column for labels of rows as Y.
  If columns of X and Y was not given, all elements are used as numerical values.
  When you want to select rows, you may use '--query'.

  Labels for X-axis are made from names of columns. labels for Y-axis are row number for deault or contents in Y column if given.

example:
  csv_plot_annotated_heatmap.py --format=html --x=B,C,D,E --y=A --show_scale --x_title=XAXIS --y_title=YAXIS test_annotated_heatmap.csv
  csv_plot_annotated_heatmap.py --format=html --x=B,C,D,E --y=A --show_scale --x_title=XAXIS --y_title=YAXIS --query="B>=10" test_annotated_heatmap.csv


</pre>
## csv_plot_bar.py
<pre>
usage: csv_plot_bar.py [-h] [-v] [--title TEXT] [--facets column[,column]]
                       [--category column] [--category_orders JSON_STRING]
                       [--barmode {group,overlay,relative}]
                       [--animation_column column[:datetime_format]]
                       [--datetime DATETIME_FORMAT] [--xrange XMIN,XMAX]
                       [--yrange YMIN,YMAX] [--log_x] [--log_y]
                       [--noautoscale] [--error_x COLUMN] [--error_y COLUMN]
                       [--output FILE] [--format {svg,png,jpg,json,html}]
                       [--packed_html] [--width WIDTH] [--height HEIGHT]
                       CSV_FILE X_COLUMN_OR_Y_COLUMNS
                       [COLUMN[,COLUMN[,COLUMN..]]]

plot bar chart

positional arguments:
  CSV_FILE              csv files to read
  X_COLUMN_OR_Y_COLUMNS
                        name of x column or names of y columns with csv format
  COLUMN[,COLUMN[,COLUMN..]]
                        names of y colums

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --title TEXT          title of chart
  --facets column[,column]
                        names of columns to make group with csv,
                        'row_facet,col_facet'
  --category column     name of column as category
  --category_orders JSON_STRING
                        orders of elements in each category, with json format
  --barmode {group,overlay,relative}
                        bar mode, default=relative
  --animation_column column[:datetime_format]
                        name of column as aimation
  --datetime DATETIME_FORMAT
                        format of x as datetime
  --xrange XMIN,XMAX    range of x
  --yrange YMIN,YMAX    range of y
  --log_x               log-scaled x axis
  --log_y               log-scaled y axis
  --noautoscale         not autoscale x or y for facets
  --error_x COLUMN      column name of error x
  --error_y COLUMN      column name of error y
  --output FILE         path of output file
  --format {svg,png,jpg,json,html}
                        format of output, default=svg
  --packed_html         whether plotly.js is included in result html file,
                        this is enable only for --format=html
  --width WIDTH         width of output
  --height HEIGHT       height of output

remark:
  plotly.express: high-level interface for data visualization  4.9.0 documentation https://plotly.com/python-api-reference/plotly.express.html

  only x_or_y_column was given without y_columns, sequence numbers are used as x values that are generated atuomaticaly.

  for animation column, colon ":" must be escaped by "". ex: "Animation\:Column".
  if datetime column was used as column for animation, format of datetime should be defined.
  see datetime  Basic date and time types  Python 3.9.4 documentation https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

example:
  csv_plot_bar.py --output=test.html test_bar.csv count
  csv_plot_bar.py --format=html --category=medal --barmode=group test_bar.csv nation count
  csv_plot_bar.py --output=test_bar_dt.html --category=medal --barmode=group --datetime="%Y-%m-%d %H:%M:%S" test_bar.csv dt count
  input:
  ,nation,medal,count
  0,South Korea,gold,24
  1,China,gold,10
  2,Canada,gold,9
  3,South Korea,silver,13
  4,China,silver,15
  5,Canada,silver,12
  6,South Korea,bronze,11
  7,China,bronze,8
  8,Canada,bronze,12


</pre>
## csv_plot_box.py
<pre>
usage: csv_plot_box.py [-h] [-v] [--title TEXT] [--facets column[,column]]
                       [--category column] [--category_orders JSON_STRING]
                       [--animation_column column[:datetime_format]]
                       [--datetime DATETIME_FORMAT] [--xrange XMIN,XMAX]
                       [--yrange YMIN,YMAX] [--log_x] [--log_y]
                       [--noautoscale] [--type {box,violin}]
                       [--mode {group,overlay}]
                       [--points {outliers,suspectedoutliers,all,False}]
                       [--output FILE] [--format {svg,png,jpg,json,html}]
                       [--packed_html] [--width WIDTH] [--height HEIGHT]
                       CSV_FILE X_COLUMN [Y_COLUMN]

plot box chart

positional arguments:
  CSV_FILE              csv files to read
  X_COLUMN              name of colum as values or x-axis
  Y_COLUMN              name of colum as values

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --title TEXT          title of chart
  --facets column[,column]
                        names of columns to make group with csv,
                        'row_facet,col_facet'
  --category column     name of column as category
  --category_orders JSON_STRING
                        orders of elements in each category, with json format
  --animation_column column[:datetime_format]
                        name of column as aimation
  --datetime DATETIME_FORMAT
                        format of x as datetime
  --xrange XMIN,XMAX    range of x
  --yrange YMIN,YMAX    range of y
  --log_x               log-scaled x axis
  --log_y               log-scaled y axis
  --noautoscale         not autoscale x or y for facets
  --type {box,violin}   box or violin
  --mode {group,overlay}
                        box mode or strip mode
  --points {outliers,suspectedoutliers,all,False}
                        mode showing points
  --output FILE         path of output file
  --format {svg,png,jpg,json,html}
                        format of output, default=svg
  --packed_html         whether plotly.js is included in result html file,
                        this is enable only for --format=html
  --width WIDTH         width of output
  --height HEIGHT       height of output

remark:

  for animation column, colon ":" must be escaped by "". ex: "Animation\:Column".
  if datetime column was used as column for animation, format of datetime should be defined.
  see datetime  Basic date and time types  Python 3.9.4 documentation https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

example:
  import plotly.express as px
  df = px.data.tips()
  df.to_csv("test_strip.csv")

  csv_plot_box.py --facets=wday --category=type --format=html test_strip.csv total time  
  csv_plot_box.py --category=type --format=html --type=violin test_strip.csv total time
  csv_plot_box.py --output=test_box_dt.html --datetime="%Y-%m-%d %H:%M:%S" test_bar.csv dt


</pre>
## csv_plot_heatmap.py
<pre>
usage: csv_plot_heatmap.py [-h] [-v] [--title TEXT] [--nbins_x INT]
                           [--nbins_y INT] [--contour]
                           [--side_hist {rug,box,violin,histogram}]
                           [--facets column[,column]]
                           [--hist_func {count,sum,avg,min,max}]
                           [--color_table {1,2,3,4,5,6,7,8,9,10,11,12}]
                           [--category_orders JSON_STRING]
                           [--animation_column column[:datetime_format]]
                           [--xrange XMIN,XMAX] [--yrange YMIN,YMAX] [--log_x]
                           [--log_y] [--noautoscale] [--output FILE]
                           [--format {svg,png,jpg,json,html}] [--packed_html]
                           [--width WIDTH] [--height HEIGHT]
                           CSV_FILE X_COLUMN Y_COLUMN [Z_COLUMN]

plot heatmap chart

positional arguments:
  CSV_FILE              csv files to read
  X_COLUMN              name of colum as x-axis
  Y_COLUMN              name of colum as y-axis
  Z_COLUMN              name of colum as z-axis

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --title TEXT          title of chart
  --nbins_x INT         number of bins for x-axis,default=10
  --nbins_y INT         number of bins for y-axis,default=10
  --contour             contour mode
  --side_hist {rug,box,violin,histogram}
                        side histogram mode
  --facets column[,column]
                        names of columns to make group with csv,
                        'row_facet,col_facet'
  --hist_func {count,sum,avg,min,max}
                        function for histogram z-axis
  --color_table {1,2,3,4,5,6,7,8,9,10,11,12}
                        color table for heat map, default=1
  --category_orders JSON_STRING
                        orders of elements in each category, with json format
  --animation_column column[:datetime_format]
                        name of column as aimation
  --xrange XMIN,XMAX    range of x
  --yrange YMIN,YMAX    range of y
  --log_x               log-scaled x axis
  --log_y               log-scaled y axis
  --noautoscale         not autoscale x or y for facets
  --output FILE         path of output file
  --format {svg,png,jpg,json,html}
                        format of output, default=svg
  --packed_html         whether plotly.js is included in result html file,
                        this is enable only for --format=html
  --width WIDTH         width of output
  --height HEIGHT       height of output

remark:
  for animation column, colon ":" must be escaped by "". ex: "Animation\:Column".
  if datetime column was used as column for animation, format of datetime should be defined.
  see datetime  Basic date and time types  Python 3.9.4 documentation https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

example:
  csv_plot_heatmap.py --xrange=0,.5 --yrange=0,.5 --format=html test_plot.csv ABC001 ABC002


</pre>
## csv_plot_histogram.py
<pre>
usage: csv_plot_histogram.py [-h] [-v] [--title TEXT] [--nbins INT]
                             [--nbin_modes {square-root,sturges,rice,doane,s_and_s,freedman_diaconis}]
                             [--side_hist {rug,box,violin,histogram}]
                             [--facets column[,column]]
                             [--hist_func {count,sum,avg,min,max}]
                             [--category column]
                             [--category_orders JSON_STRING]
                             [--animation_column column[:datetime_format]]
                             [--datetime DATETIME_FORMAT] [--xrange XMIN,XMAX]
                             [--yrange YMIN,YMAX] [--log_x] [--log_y]
                             [--noautoscale] [--output FILE]
                             [--format {svg,png,jpg,json,html}]
                             [--packed_html] [--width WIDTH] [--height HEIGHT]
                             [--pareto_chart]
                             [--pareto_sort_mode {count,axis}]
                             CSV_FILE X_COLUMN [Y_COLUMN]

plot histogram chart with counting values

positional arguments:
  CSV_FILE              csv files to read
  X_COLUMN              name of colum as x-axis
  Y_COLUMN              name of colum as weight of histogram

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --title TEXT          title of chart
  --nbins INT           number of bins,default=10
  --nbin_modes {square-root,sturges,rice,doane,s_and_s,freedman_diaconis}
                        method to evaluate number of bins. if given, '--nbins'
                        is ignored.
  --side_hist {rug,box,violin,histogram}
                        side histogram mode
  --facets column[,column]
                        names of columns to make group with csv,
                        'row_facet,col_facet'
  --hist_func {count,sum,avg,min,max}
                        function for histogram z-axis
  --category column     name of column as category
  --category_orders JSON_STRING
                        orders of elements in each category, with json format
  --animation_column column[:datetime_format]
                        name of column as aimation
  --datetime DATETIME_FORMAT
                        format of x as datetime
  --xrange XMIN,XMAX    range of x
  --yrange YMIN,YMAX    range of y
  --log_x               log-scaled x axis
  --log_y               log-scaled y axis
  --noautoscale         not autoscale x or y for facets
  --output FILE         path of output file
  --format {svg,png,jpg,json,html}
                        format of output, default=svg
  --packed_html         whether plotly.js is included in result html file,
                        this is enable only for --format=html
  --width WIDTH         width of output
  --height HEIGHT       height of output
  --pareto_chart        pareto chart mode
  --pareto_sort_mode {count,axis}
                        sort mode for pareto mode, default=asscending count

remark:
  the column for '--facet' and '--ctegory' should have few uni values.

  If '--xrange' was given, valuse in the column was clipped into the range and plotted with bins given by '--nbins'.

  for '--pareto_chart', only followings are available
      '--xrange', '--yrange', '--nbins', '--output', '--format', '--with', '--height', '--packed_html'
  '--pareto_sort_mode=axis' may be usefull to estimate threhold.

  for animation column, colon ":" must be escaped by "". ex: "Animation\:Column".
  if datetime column was used as column for animation, format of datetime should be defined.
  see datetime  Basic date and time types  Python 3.9.4 documentation https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

  about '--nbin_mode', see Histogram - Wikipedia https://en.wikipedia.org/wiki/Histogram .
  NOTE 's_and_s' means Shimazaki and Shinomoto's choice.

example:
  csv_plot_histogram.py --nbins=50 --category="ABC004" --xrange=0.4,0.6 --output=test_plot_hist.html test_plot.csv  "ABC001" "ABC002"
  csv_plot_histogram.py --nbins=50 --category="ABC004" --side_hist=rug --output=test_plot_hist.html test_plot.csv  "ABC001" "ABC002"
  csv_plot_histogram.py --nbins=50 --category="ABC004" --side_hist=rug --log_y --xrange=0.4,0.6 --output=test_plot_hist.html test_plot.csv "ABC001" "ABC002"
  csv_plot_histogram.py --nbin_mode="square-root" --output=test_plot_hist.html test_plot.csv "ABC001" "ABC002"

  csv_plot_histogram.py --output=test.html --pareto_chart --nbins=100 a10.csv value
  csv_plot_histogram.py --output=test.html --pareto_chart --pareto_sort_mode=axis --nbins=100 a10.csv value
  csv_plot_histogram.py --output=test_hist_dt.html --datetime="%Y-%m-%d %H:%M:%S" test_bar.csv dt


</pre>
## csv_plot_line.py
<pre>
usage: csv_plot_line.py [-h] [-v] [--title TEXT] [--facets column[,column]]
                        [--category column] [--category_orders JSON_STRING]
                        [--animation_column column[:datetime_format]]
                        [--datetime DATETIME_FORMAT] [--xrange XMIN,XMAX]
                        [--yrange YMIN,YMAX] [--log_x] [--log_y]
                        [--noautoscale] [--error_x COLUMN] [--error_y COLUMN]
                        [--output FILE] [--format {svg,png,jpg,json,html}]
                        [--packed_html] [--width WIDTH] [--height HEIGHT]
                        CSV_FILE X_COLUMN_OR_Y_COLUMNS
                        [COLUMN[,COLUMN[,COLUMN..]]]

plot line chart

positional arguments:
  CSV_FILE              csv files to read
  X_COLUMN_OR_Y_COLUMNS
                        name of x column or names of y columns with csv format
  COLUMN[,COLUMN[,COLUMN..]]
                        names of y colums

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --title TEXT          title of chart
  --facets column[,column]
                        names of columns to make group with csv,
                        'row_facet,col_facet'
  --category column     name of column as category
  --category_orders JSON_STRING
                        orders of elements in each category, with json format
  --animation_column column[:datetime_format]
                        name of column as aimation
  --datetime DATETIME_FORMAT
                        format of x as datetime
  --xrange XMIN,XMAX    range of x
  --yrange YMIN,YMAX    range of y
  --log_x               log-scaled x axis
  --log_y               log-scaled y axis
  --noautoscale         not autoscale x or y for facets
  --error_x COLUMN      column name of error x
  --error_y COLUMN      column name of error y
  --output FILE         path of output file
  --format {svg,png,jpg,json,html}
                        format of output, default=svg
  --packed_html         whether plotly.js is included in result html file,
                        this is enable only for --format=html
  --width WIDTH         width of output
  --height HEIGHT       height of output

remark:
  plotly.express: high-level interface for data visualization  4.9.0 documentation https://plotly.com/python-api-reference/plotly.express.html

  only x_or_y_column was given without y_columns, sequence numbers are used as x values that are generated atuomaticaly.

  for animation column, colon ":" must be escaped by "". ex: "Animation\:Column".
  if datetime column was used as column for animation, format of datetime should be defined.
  see datetime  Basic date and time types  Python 3.9.4 documentation https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

example:
  csv_plot_line.py --facets=COL_0006 --output=test.html big_sample_arb.csv COL_0008,COL_0033,COL_0097
  csv_plot_line.py --facets=COL_0006 --format html big_sample_arb.csv COL_0000 COL_0008,COL_0033,COL_0097
  csv_plot_line.py --output=test_line_dt.html --datetime="%Y-%m-%d %H:%M:%S" test_bar.csv dt count


</pre>
## csv_plot_line_3d.py
<pre>
usage: csv_plot_line_3d.py [-h] [-v] [--title TEXT] [--category column]
                           [--category_orders JSON_STRING]
                           [--animation_column column[:datetime_format]]
                           [--xrange XMIN,XMAX] [--yrange YMIN,YMAX]
                           [--zrange ZMIN,ZMAX] [--log_x] [--log_y] [--log_z]
                           [--error_x COLUMN] [--error_y COLUMN]
                           [--error_z COLUMN] [--output FILE]
                           [--format {svg,png,jpg,json,html}] [--packed_html]
                           [--width WIDTH] [--height HEIGHT]
                           CSV_FILE X_COLUMN Y_COLUMN Z_COLUMN

plot 3d line chart

positional arguments:
  CSV_FILE              csv files to read
  X_COLUMN              name of x column
  Y_COLUMN              name of y column
  Z_COLUMN              name of z column

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --title TEXT          title of chart
  --category column     name of column as category
  --category_orders JSON_STRING
                        orders of elements in each category, with json format
  --animation_column column[:datetime_format]
                        name of column as aimation
  --xrange XMIN,XMAX    range of x
  --yrange YMIN,YMAX    range of y
  --zrange ZMIN,ZMAX    range of z
  --log_x               log-scaled x axis
  --log_y               log-scaled y axis
  --log_z               log-scaled z axis
  --error_x COLUMN      column name of error x
  --error_y COLUMN      column name of error y
  --error_z COLUMN      column name of error z
  --output FILE         path of output file
  --format {svg,png,jpg,json,html}
                        format of output, default=svg
  --packed_html         whether plotly.js is included in result html file,
                        this is enable only for --format=html
  --width WIDTH         width of output
  --height HEIGHT       height of output

remark:
  plotly.express.line_3d  4.11.0 documentation https://plotly.com/python-api-reference/generated/plotly.express.line_3d.html#plotly.express.line_3d

  for animation column, colon ":" must be escaped by "". ex: "Animation\:Column".
  if datetime column was used as column for animation, format of datetime should be defined.
  see datetime  Basic date and time types  Python 3.9.4 documentation https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

example:
  csv_plot_line_3d.py --format=html --category=COL_0006 big_sample_arb.csv COL_0008 COL_0033 COL_0097


</pre>
## csv_plot_parallel_coordinates.py
<pre>
usage: csv_plot_parallel_coordinates.py [-h] [-v] [--title TEXT] [--discrete]
                                        [--ignore_key]
                                        [--color_table {1,2,3,4,5,6,7,8,9,10,11,12}]
                                        [--xrange XMIN,XMAX]
                                        [--animation_column column[:datetime_format]]
                                        [--output FILE]
                                        [--format {svg,png,jpg,json,html}]
                                        [--packed_html] [--width WIDTH]
                                        [--height HEIGHT]
                                        CSV_FILE KEY COLUMNS

plot parallel_coordinates chart

positional arguments:
  CSV_FILE              csv files to read
  KEY                   name of key column
  COLUMNS               names of colums

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --title TEXT          title of chart
  --discrete            discrete mode
  --ignore_key          ignore key column
  --color_table {1,2,3,4,5,6,7,8,9,10,11,12}
                        color table for heat map, default=1
  --xrange XMIN,XMAX    range of x
  --animation_column column[:datetime_format]
                        name of column as aimation
  --output FILE         path of output file
  --format {svg,png,jpg,json,html}
                        format of output, default=svg
  --packed_html         whether plotly.js is included in result html file,
                        this is enable only for --format=html
  --width WIDTH         width of output
  --height HEIGHT       height of output

remark:
  key colmun must have only numeric values.
  all others columns has numeric values.
  if columns has discrete values, then use '--discrete'.

  for animation column, colon ":" must be escaped by "". ex: "Animation\:Column".
  if datetime column was used as column for animation, format of datetime should be defined.
  see datetime  Basic date and time types  Python 3.9.4 documentation https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

example:
  csv_plot_parallel_coordinates.py --format=html big_sample_arb.csv COL_0097 COL_0008,COL_0033
  csv_plot_parallel_coordinates.py --format=html --discrete big_sample_arb.csv COL_0008 COL_0006,COL_0002,COL_0023


</pre>
## csv_plot_polar.py
<pre>
usage: csv_plot_polar.py [-h] [-v] [--title TEXT] [--category column]
                         [--category_orders JSON_STRING] [--rrange RMIN,RMAX]
                         [--thrange THMIN,THMAX] [--log_r]
                         [--direction {counterclockwise,clockwise}]
                         [--start_angle START_ANGLE] [--clock]
                         [--type {scatter,line,bar}] [--line_close]
                         [--line_shape {linear,spline}]
                         [--animation_column column[:datetime_format]]
                         [--output FILE] [--format {svg,png,jpg,json,html}]
                         [--packed_html] [--width WIDTH] [--height HEIGHT]
                         CSV_FILE R_COLUMN THETA_COLUMN [WEIGHT_COLUMN]

plot polar chart

positional arguments:
  CSV_FILE              csv files to read
  R_COLUMN              name of colum as radius
  THETA_COLUMN          name of colum as theta
  WEIGHT_COLUMN         name of colum as weight

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --title TEXT          title of chart
  --category column     name of column as category
  --category_orders JSON_STRING
                        orders of elements in each category, with json format
  --rrange RMIN,RMAX    range of radius
  --thrange THMIN,THMAX
                        range of theta
  --log_r               log-scaled radius
  --direction {counterclockwise,clockwise}
                        direction of rotation
  --start_angle START_ANGLE
                        angle for starting plot [deg]
  --clock               equal to --start_angle=90 --direction='clockwise': '--
                        start_angle'and '--direction' are ignored.
  --type {scatter,line,bar}
                        chart type
  --line_close          line closing mode, available for only line chart
  --line_shape {linear,spline}
                        line shape, available for only line chart
  --animation_column column[:datetime_format]
                        name of column as aimation
  --output FILE         path of output file
  --format {svg,png,jpg,json,html}
                        format of output, default=svg
  --packed_html         whether plotly.js is included in result html file,
                        this is enable only for --format=html
  --width WIDTH         width of output
  --height HEIGHT       height of output

remark:

  for animation column, colon ":" must be escaped by "". ex: "Animation\:Column".
  if datetime column was used as column for animation, format of datetime should be defined.
  see datetime  Basic date and time types  Python 3.9.4 documentation https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

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
  csv_plot_polar.py --format=html --category=strength --start_angle=90 --direction="clockwise"                     test_polar.csv frequency direction frequency
  csv_plot_polar.py --format=html --type=line --category=strength --line_close --line_shape=spline                     --start_angle=90 --direction="clockwise" test_polar.csv frequency direction frequency


</pre>
## csv_plot_quiver.py
<pre>
usage: csv_plot_quiver.py [-h] [-v] [--title TEXT] [--x_title TEXT]
                          [--y_title TEXT] [--arrow_size ASIZE]
                          [--line_width LWIDTH] [--streamline NGRIDX,NGRIDY]
                          [--xrange XMIN,XMAX] [--yrange YMIN,YMAX] [--log_x]
                          [--log_y] [--output FILE]
                          [--format {svg,png,jpg,json,html}] [--packed_html]
                          [--width WIDTH] [--height HEIGHT]
                          CSV_FILE X_COLUMN Y_COLUMN U_COLUMN V_COLUMN

plot quiver chart

positional arguments:
  CSV_FILE              csv files to read
  X_COLUMN              name of x column
  Y_COLUMN              name of y column
  U_COLUMN              name of u column
  V_COLUMN              name of v column

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --title TEXT          title of chart
  --x_title TEXT        title of x axis
  --y_title TEXT        title of y axis
  --arrow_size ASIZE    size factor of arrow,[0,1]
  --line_width LWIDTH   width of line of arrow
  --streamline NGRIDX,NGRIDY
                        [exp]stream line mode
  --xrange XMIN,XMAX    range of x
  --yrange YMIN,YMAX    range of y
  --log_x               log-scaled x axis
  --log_y               log-scaled y axis
  --output FILE         path of output file
  --format {svg,png,jpg,json,html}
                        format of output, default=svg
  --packed_html         whether plotly.js is included in result html file,
                        this is enable only for --format=html
  --width WIDTH         width of output
  --height HEIGHT       height of output

remark:
  Quiver Plots | Python | Plotly https://plotly.com/python/quiver-plots/

example:
  csv_plot_quiver.py --title="sample of quiver chart" --format=html test_quiver.csv X Y U V
  csv_plot_quiver.py --title="sample of quiver chart" --streamline=10,10 --format=html test_quiver.csv X Y U V


</pre>
## csv_plot_scatter.py
<pre>
usage: csv_plot_scatter.py [-h] [-v] [--title TEXT]
                           [--side_hist {rug,box,violin,histogram}]
                           [--facets column[,column]] [--category column]
                           [--category_orders JSON_STRING]
                           [--size_column column]
                           [--animation_column column[:datetime_format]]
                           [--trendline {ols,lowess}]
                           [--x_datetime DATETIME_FORMAT]
                           [--y_datetime DATETIME_FORMAT] [--xrange XMIN,XMAX]
                           [--yrange YMIN,YMAX] [--log_x] [--log_y]
                           [--noautoscale] [--error_x COLUMN]
                           [--error_y COLUMN] [--output FILE]
                           [--format {svg,png,jpg,json,html}] [--packed_html]
                           [--width WIDTH] [--height HEIGHT]
                           CSV_FILE X_COLUMN Y_COLUMN

plot scatter chart

positional arguments:
  CSV_FILE              csv files to read
  X_COLUMN              name of x column
  Y_COLUMN              name of y column

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --title TEXT          title of chart
  --side_hist {rug,box,violin,histogram}
                        side histogram mode
  --facets column[,column]
                        names of columns to make group with csv,
                        'row_facet,col_facet'
  --category column     name of column as category
  --category_orders JSON_STRING
                        orders of elements in each category, with json format
  --size_column column  name of column as size of symbol
  --animation_column column[:datetime_format]
                        name of column as aimation
  --trendline {ols,lowess}
                        trendline mode
  --x_datetime DATETIME_FORMAT
                        format of x as datetime
  --y_datetime DATETIME_FORMAT
                        format of y as datetime
  --xrange XMIN,XMAX    range of x
  --yrange YMIN,YMAX    range of y
  --log_x               log-scaled x axis
  --log_y               log-scaled y axis
  --noautoscale         not autoscale x or y for facets
  --error_x COLUMN      column name of error x
  --error_y COLUMN      column name of error y
  --output FILE         path of output file
  --format {svg,png,jpg,json,html}
                        format of output, default=svg
  --packed_html         whether plotly.js is included in result html file,
                        this is enable only for --format=html
  --width WIDTH         width of output
  --height HEIGHT       height of output

remark:
  plotly.express: high-level interface for data visualization  4.9.0 documentation https://plotly.com/python-api-reference/plotly.express.html

  trendline mode:
     ols=Ordinary Least Squares regression line will be drawn for each discrete-color/symbol group
     lowess=a Locally Weighted Scatterplot Smoothing line will be drawn for each discrete-color/symbol group.
     see plotly.express.scatter  4.10.0 documentation https://plotly.com/python-api-reference/generated/plotly.express.scatter.html

  for animation column, colon ":" must be escaped by "". ex: "Animation\:Column".
  if datetime column was used as column for animation, format of datetime should be defined.
  see datetime  Basic date and time types  Python 3.9.4 documentation https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

  statsmodels

example:
  csv_plot_scatter.py --format=html --category=COL_0006  --size_column=COL_0097 --side_hist=rug big_sample_arb.csv COL_0008 COL_0003 


</pre>
## csv_plot_scatter_3d.py
<pre>
usage: csv_plot_scatter_3d.py [-h] [-v] [--title TEXT] [--category column]
                              [--category_orders JSON_STRING]
                              [--size_column column]
                              [--animation_column column[:datetime_format]]
                              [--xrange XMIN,XMAX] [--yrange YMIN,YMAX]
                              [--zrange ZMIN,ZMAX] [--log_x] [--log_y]
                              [--log_z] [--error_x COLUMN] [--error_y COLUMN]
                              [--error_z COLUMN] [--output FILE]
                              [--format {svg,png,jpg,json,html}]
                              [--packed_html] [--width WIDTH]
                              [--height HEIGHT]
                              CSV_FILE X_COLUMN Y_COLUMN Z_COLUMN

plot 3d scatter chart

positional arguments:
  CSV_FILE              csv files to read
  X_COLUMN              name of x column
  Y_COLUMN              name of y column
  Z_COLUMN              name of z column

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --title TEXT          title of chart
  --category column     name of column as category
  --category_orders JSON_STRING
                        orders of elements in each category, with json format
  --size_column column  name of column as size of symbol
  --animation_column column[:datetime_format]
                        name of column as aimation
  --xrange XMIN,XMAX    range of x
  --yrange YMIN,YMAX    range of y
  --zrange ZMIN,ZMAX    range of z
  --log_x               log-scaled x axis
  --log_y               log-scaled y axis
  --log_z               log-scaled z axis
  --error_x COLUMN      column name of error x
  --error_y COLUMN      column name of error y
  --error_z COLUMN      column name of error z
  --output FILE         path of output file
  --format {svg,png,jpg,json,html}
                        format of output, default=svg
  --packed_html         whether plotly.js is included in result html file,
                        this is enable only for --format=html
  --width WIDTH         width of output
  --height HEIGHT       height of output

remark:
  plotly.express.scatter_3d  4.11.0 documentation https://plotly.com/python-api-reference/generated/plotly.express.scatter_3d.html

  for animation column, colon ":" must be escaped by "". ex: "Animation\:Column".
  if datetime column was used as column for animation, format of datetime should be defined.
  see datetime  Basic date and time types  Python 3.9.4 documentation https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

example:
  csv_plot_scatter_3d.py --format=html --category=COL_0006 big_sample_arb.csv COL_0008 COL_0033 COL_0097
  csv_plot_scatter_3d.py --format=html --category=COL_0006 --size_column=COL_0107 big_sample_arb.csv COL_0008 COL_0033 COL_0097


</pre>
## csv_plot_scatter_matrix.py
<pre>
usage: csv_plot_scatter_matrix.py [-h] [-v] [--title TEXT] --columns
                                  COLUMNS,COLUMNS[,COLUMNS...]
                                  [--category COLUMN]
                                  [--category_orders JSON_STRING]
                                  [--output FILE]
                                  [--format {svg,png,jpg,json,html}]
                                  [--packed_html] [--width WIDTH]
                                  [--height HEIGHT]
                                  CSV_FILE

plot scatter matrix

positional arguments:
  CSV_FILE              csv files to read

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --title TEXT          title of chart
  --columns COLUMNS,COLUMNS[,COLUMNS...]
                        list of names of columns with csv
  --category COLUMN     name of column to make group
  --category_orders JSON_STRING
                        orders of elements in each category, with json format
  --output FILE         path of output file
  --format {svg,png,jpg,json,html}
                        format of output, default=svg
  --packed_html         whether plotly.js is included in result html file,
                        this is enable only for --format=html
  --width WIDTH         width of output
  --height HEIGHT       height of output

example:
  csv_plot_scatter_matrix.py --columns="ABC001","ABC002","ABC003" --category="ABC004" --output=test.png test_plot.csv


</pre>
## csv_plot_strip.py
<pre>
usage: csv_plot_strip.py [-h] [-v] [--title TEXT] [--facets column[,column]]
                         [--category column] [--category_orders JSON_STRING]
                         [--animation_column column[:datetime_format]]
                         [--datetime DATETIME_FORMAT] [--xrange XMIN,XMAX]
                         [--yrange YMIN,YMAX] [--log_x] [--log_y]
                         [--noautoscale] [--mode {group,overlay}]
                         [--output FILE] [--format {svg,png,jpg,json,html}]
                         [--packed_html] [--width WIDTH] [--height HEIGHT]
                         CSV_FILE X_COLUMN [Y_COLUMN]

plot strip chart

positional arguments:
  CSV_FILE              csv files to read
  X_COLUMN              name of colum as x-axis
  Y_COLUMN              name of colum as weight of histogram

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --title TEXT          title of chart
  --facets column[,column]
                        names of columns to make group with csv,
                        'row_facet,col_facet'
  --category column     name of column as category
  --category_orders JSON_STRING
                        orders of elements in each category, with json format
  --animation_column column[:datetime_format]
                        name of column as aimation
  --datetime DATETIME_FORMAT
                        format of x as datetime
  --xrange XMIN,XMAX    range of x
  --yrange YMIN,YMAX    range of y
  --log_x               log-scaled x axis
  --log_y               log-scaled y axis
  --noautoscale         not autoscale x or y for facets
  --mode {group,overlay}
                        strip mode
  --output FILE         path of output file
  --format {svg,png,jpg,json,html}
                        format of output, default=svg
  --packed_html         whether plotly.js is included in result html file,
                        this is enable only for --format=html
  --width WIDTH         width of output
  --height HEIGHT       height of output

remark:
  Using a Strip Chart - Accendo Reliability https://accendoreliability.com/using-strip-chart/
  When there is scant data a histogram or box plot just is not informative. 
  This is a great use for a one dimensional scatter plot, dot plot, or a what is called a strip chart in R.

  for animation column, colon ":" must be escaped by "". ex: "Animation\:Column".
  if datetime column was used as column for animation, format of datetime should be defined.
  see datetime  Basic date and time types  Python 3.9.4 documentation https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

example:
  import plotly.express as px
  df = px.data.tips()
  df.to_csv("test_strip.csv")

  csv_plot_strip.py --facets=wday --category=type --format=html test_strip.csv total time
  csv_plot_strip.py --output=test_strip_dt.html --datetime="%Y-%m-%d %H:%M:%S" test_bar.csv dt count
</pre>

## csv_plot_csvtk.sh
<pre>
plot histogram by graphical character.
Usage: csv_plot_csvtk.sh [-s] csv_file x_column y_column [group_column]
Usage: csv_plot_csvtk.sh -t csv_file column
arguments:
  csv_file    : path of csv file
  x_column    : name of column for x
  y_column    : name of column for y
  column      : name of column to make histogram
  group_column: name of column for grouping

options:
  -s : scatter plot
  -t : histogram mode for one colun


example:
  csv_plot_csvtk.sh -s big_sample_arb.csv COL_0008 COL_0033 COL_0006
  csv_plot_csvtk.sh -t test_plot.csv COL_0000



</pre>
## csv_plot_subplot_line.sh
<pre>
plot multi-columns in csv file as subplot of line chart
Usage: csv_plot_subplot_line.sh [-o output_html] [-t tile] [-p options_of_csv_plot_line] csv_file key_column plot_colun[,plot_column...]
options:
 -o output_html: default={prefix of input file}.html
 -t title : title of chart
 -p options: options of csv_plot_line.py by string 

example:
  csv_plot_subplot_line.sh -t "a b c" -p "--log_y" test_plot.csv ABC000 ABC001,ABC002,ABC003

</pre>
