<!-- File: COMMAND_LIST.md                      -->
<!-- Description:               -->
<!-- Copyright (C) 2021 by m.na.akei   -->
<!-- Time-stamp: "2021-01-09 11:29:17" -->

<!-- START doctoc -->
<!-- END doctoc -->

# コマンドリスト


各ディレクトリに収納されているコマンドのリストを下表に示した。
既存のツールの単なるラッパツールに なっているものも含まれる。


## csv_plot

| command name                     | description                               | description                                                           |
|----------------------------------|-------------------------------------------|-----------------------------------------------------------------------|
| csv_plot_annotated_heatmap.py    | create heatmap chart for x-y matrix data  | XY行列情報を持つCSVから数値表示を伴ったヒートマップを生成する         |
| csv_plot_bar.py                  | plot bar chart                            | CSVの指定列からバーチャートを生成する                                 |
| csv_plot_box.py                  | plot box chart                            | CSVの指定列からボックスチャートを生成する                             |
| csv_plot_heatmap.py              | plot heatmap chart                        | CSVの指定列からヒートマップを生成する                                 |
| csv_plot_histogram.py            | plot histogram chart with counting values | CSVの指定列からヒストグラムチャートを生成する                         |
| csv_plot_line.py                 | plot line chart                           | CSVの指定列からラインチャートを生成する                               |
| csv_plot_line_3d.py              | plot 3d line chart                        | CSVの指定列から3次元のラインチャートを生成する                        |
| csv_plot_parallel_coordinates.py | plot parallel_coordinates chart           | CSVの指定列からパラレルチャートを生成する                             |
| csv_plot_polar.py                | plot polar chart                          | CSVの指定列からポーラーチャートを生成する                             |
| csv_plot_quiver.py               | plot quiver chart                         | CSVの指定列からカイバーチャートを生成する                             |
| csv_plot_scatter.py              | plot scatter chart                        | CSVの指定列から散布チャートを生成する                                 |
| csv_plot_scatter_3d.py           | plot 3d scatter chart                     | CSVの指定列から3次元の散布チャートを生成する                          |
| csv_plot_scatter_matrix.py       | plot scatter matrix                       | CSVの指定列から散布行列チャートを生成する                             |
| csv_plot_strip.py                | plot strip chart                          | CSVの指定列からストリップチャートを生成する                           |
| csv_plot_csvtk.sh                | plot histogram by graphical character.    | CSVの指定列からテキストコンソールにヒストグラムチャートを生成表示する |


## csv_utility

| command name              | description                                                                 | description                                                            |
|---------------------------|-----------------------------------------------------------------------------|------------------------------------------------------------------------|
| csv_cut.sh                | print range of rows and range of columns in csv file                        | CSVから指定される行範囲、列範囲を出力する                              |
| csv_dtype.sh              | to estimate data type of each column                                        | CSVの列の推定データ型について出力する                                  |
| csv_dummy.sh              | make simple dummy record with csv format                                    | 要素の値を行番号／列番号をHex表記した指定する行数／列数のCSVを生成する |
| csv_function.sh           | replace contents of columns with values that were processed by 'function'.  | シェルスクリプトによる要素値の置き換え出力を行う                       |
| csv_get_col_index.sh      | to get index of column  or name of column with 1-base                       | CSVの列名または列番号を指定して、列番号または列名を出力する            |
| csv_head.sh               | command like ‘head’ for csv.                                              | headコマンドのCSV版                                                    |
| csv_hist_console.sh       | plot histogram by ascii character.                                          | コンソール画面でヒストグラム表示を行う                                 |
| csv_join.sh               | join two csv file into one csv file                                         | XSVを用いたCSVファイルの列方向の結合                                   |
| csv_matrix.sh             | convert matrix data into (x,y,v).                                           | 行列形式のCSVデータを(X,Y,V)形式へ変換する                             |
| csv_print.sh              | to print contents around given (row, col) in csv file.                      | CSVの指定する行／列の周辺を含めた要素値の出力を行う                    |
| csv_print_head.sh         | to print names of columns in csv file                                       | CSVの列名リストを出力する                                              |
| csv_search_rc.sh          | to search keyword in csv file and to return the position:(row, col)         | CSVの要素値を検索し、行番号／列番号を出力する                          |
| csv_split_columns.sh      | to split ONE csv file into some csv files,  that may have too many columns. | CSVを指定列数で列方向で分割する                                        |
| csv_sqlite_insert.sh      | inset contents of csv file into sqlitDB                                     | CSVをSQLite3 DBへ変換する。                                            |
| csv_stack.sh              | simply append csv files according to columns or rows.                       | 複数のCSVを行方向または列方向に結合する                                |
| csv_status_xsv.sh         | print status of each column by 'xsv'                                        | CSVの各列の要素値の統計情報を出力する(xsv版)                           |
| csv_to_db_csvkit.sh       | To insret contents of csv file into db by csvkit                            | CSVの内容をDBへ挿入する(csvkit版)                                      |
| csv_to_db_shell.sh        | to insert csv data into database                                            | CSVの内容をDBへ挿入する                                                |
| csv_to_html.sh            | convert csv file into html format                                           | CSVの内容をHTML Tableとして出力する                                    |
| csv_wc.sh                 | command like ‘wc’ for csv                                                 | wcコマンドのCSV版                                                      |
| csv_columns_summary.py    | statistics summary for each colunm with CSV format                          | CSVの各列の要素値の統計情報を出力する                                  |
| csv_combine.py            | complement the defect of datas with csv datas,  element-wise                | CSVの欠損値を他のCSVで補完する                                         |
| csv_correlation.py        | evaluate cross/auto correlation between columns                             | CSVの列間の相関を算出する                                              |
| csv_crosstable.py         | make cross-matching table from csv file                                     | CSVの列間のクロス行列を算出する                                        |
| csv_dummy.py              | generate dummy data of csv                                                  | CSVツール評価用のダミー用CSVを生成する                                 |
| csv_histogram.py          | make histogram from csv file                                                | CSVの指定列のヒストグラムデータを出力する                              |
| csv_lmfit.py              | fitting function to data in csv file                                        | CSVの指定列に対してPython lmfitを用いたフィッティングを行う            |
| csv_meltpivot.py          | melting or pivoting csv file                                                | CSVの指定列に対してPivotまたはMeltを行う                               |
| csv_multiindex_columns.py | handle multiindex columns csv                                               | マルチインデックス形式の列名を持つCSVの取り扱い                        |
| csv_print_html.py         | print html table made of csv with estimation                                | CSVを最大値／最小値のマーキングなどを行いHTMLとして出力する            |
| csv_print_html_Oia.py     | print html table made of csv with estimation                                | テキストデータを持つCSVのカラムを見やすくHTMLとして出力する            |
| csv_print_html_tl.py      | print html table made of csv with estimation                                | 時刻情報とテキストデータを持つCSVの語句の時刻分布をHTMLとして出力する  |
| csv_query.py              | do query for CSV data                                                       | CSVに対して指定条件による行選択を行う                                  |
| csv_sample.py             | derive sample records from big csv file                                     | CSVからサンプリングされた行を選択して出力する                          |
| csv_stack_trime.py        | split one column  that has multiple meaning  into some columns              | CSVの指定列を複数の列に分割する                                        |
| csv_status.py             | to derive statitical information for each columns                           | CSVの列の統計情報を出力する                                            |
| csv_trimtime.py           | triming columns that have time data                                         | CSVの時刻情報を持つ列の操作を行う                                      |
| csv_uty.py                | utility for CSV file                                                        | CSVに対して各種様々な処理を行う                                        |
| csv_window_rolling.py     | do rolling columns data,  like as moving-average                            | CSVの列に対して移動平均のようなWindow処理を行う                        |
| csv_write_excel.py        | write csv to ms-excel file with images                                      | CSVをExcelに変換する、画像情報があれば埋め込みを行う                   |



<!-- ------------------ -->
<!-- Local Variables:   -->
<!-- mode: markdown     -->
<!-- coding: utf-8-unix -->
<!-- End:               -->
