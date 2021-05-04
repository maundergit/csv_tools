## csv_columns_summary.py
<pre>
usage: csv_columns_summary.py [-h] [-v] [--columns COLUMN[,COLUMN...]]
                              [--function {all,count,sum,avg,min,max,std,median}]
                              [--count STRING] [--output FILE]
                              CSV_FILE

statistics summary for each colunm with CSV format

positional arguments:
  CSV_FILE              files to read, if empty, stdin is used

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --columns COLUMN[,COLUMN...]
                        columns to do function, default=all columns that have
                        numeric values
  --function {all,count,sum,avg,min,max,std,median}
                        function to do
  --count STRING        count of given value. if given, '--function' is
                        ignored.
  --output FILE         path of output file, default=stdout

example:
  csv_columns_summary.py --function=sum --columns=A,B test1.csv
  csv_columns_summary.py --count=1 test1.csv
  csv_columns_summary.py --function=all --columns=A,B test1.csv| csvlook -I
| columns | count | sum | avg                | min | max | std                | median |
| ------- | ----- | --- | ------------------ | --- | --- | ------------------ | ------ |
| A       | 2.0   | 5.0 | 1.6666666666666667 | 0.0 | 4.0 | 2.0816659994661326 | 1.0    |
| B       | 2.0   | 7.0 | 2.3333333333333335 | 0.0 | 5.0 | 2.5166114784235836 | 2.0    |


</pre>
## csv_combine.py
<pre>
usage: csv_combine.py [-h] [-v]
                      [--mode {first,bigger,smaller,add,sub,mul,div,mod,pow,lt,le,gt,ge,ne,eq,function}]
                      [--function EXP] [--prologe CODE;[CODE;CODE;...]]
                      [--boolean_by_number] [--output_file FILE]
                      CSV_FILE CSV_FILE_or_VALUE

complement the defect of datas with csv datas, element-wise

positional arguments:
  CSV_FILE              first csv file to complement
  CSV_FILE_or_VALUE     second csv file or scalar float value

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --mode {first,bigger,smaller,add,sub,mul,div,mod,pow,lt,le,gt,ge,ne,eq,function}
                        combine mode
  --function EXP        lambda function for function mode
  --prologe CODE;[CODE;CODE;...]
                        pieces of python code to pre-load, for use in
                        expression of '--function'.
  --boolean_by_number   for logical results, use 1/0 instead of True/False
  --output_file FILE    path of output file,default=stdout

remark:
  This processes columns that have only numeric values.

  The bigger mode, smaller mode and etc are available for columns that have numeric values, others are done by combine_first.
  At the compare modes(lt,gt,and so on), NaN leads into False as result, always.

  About function that was given by '--function', that has two arguments of pandas.Series. see document of pandas.DataFrame.combine:
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.combine.html#pandas.DataFrame.combine
  When you use '--function', you may use '--prologe' to load external module:
    ex. '--prologe="import numpy as np;"' or '--prologe="import your_module;"'

    | mode     | numeric only | description                                   |
    | -------- | ------------ | --------------------------------------------- |
    | first    |              | combine_first                                 |
    | bigger   | O            | select bigger                                 |
    | smaller  | O            | select smaller                                |
    | function | O            | to do given function                          |
    | add      | O            | adding                                        |
    | sub      | O            | subtructing                                   |
    | mul      | O            | multipling                                    |
    | div      | O            | dividing                                      |
    | mod      | O            | modulo                                        |
    | pow      | O            | power                                         |
    | lt       | O            | results of 'less than' are True/False         |
    | le       | O            | results of 'less than equal' are True/False   |
    | gt       | O            | results of 'greater than' are True/False      |
    | ge       | O            | results of 'grater than equal' are True/False |
    | ne       | O            | results of 'not equal' are True/False         |
    | eq       | O            | results of 'equal' are True/False             |

  Second argument is a path of a second csv file or scalar float value.
  When scala value is given, second csv will be created with the same shape as first csv and have given value in all elements.
  Because of inefficiently, you should not use scala value as second argument for big csv data.

example:
  csv_combine.py --mode bigger t1.csv t2.csv| csvlook -I
  | A   | B   | C | D |
  | --- | --- | - | - |
  | 1.0 | 1.0 | 1 | a |
  | 3.0 | 4.0 | 5 | b |
  | 5.0 | 5.0 | 3 | c |
  | 6.0 |     | 4 | d |

  csv_combine.py --mode smaller t1.csv t2.csv| csvlook -I
  | A   | B   | C | D |
  | --- | --- | - | - |
  | 0.0 | 0.0 | 0 | a |
  | 2.0 | 2.0 | 0 | b |
  | 3.0 | 5.0 | 3 | c |
  | 6.0 |     | 4 | d |

  csv_combine.py --mode function --function "lambda s1,s2: s1 if s1.sum() > s2.sum() else s2" t1.csv t2.csv |csvlook -I
  | A   | B   | C | D |
  | --- | --- | - | - |
  | 0.0 | 1.0 | 1 | a |
  | 3.0 | 4.0 | 0 | b |
  | 5.0 | 5.0 | 3 | c |
  | 6.0 |     | 4 | d |

  csvlook -I t1.csv
  | A | B | C | D |
  | - | - | - | - |
  | 1 | 0 | 1 | a |
  | 2 | 2 | 0 | b |
  | 3 |   | 3 |   |
  |   |   | 4 | d |

  csvlook -I t2.csv
  | A | B | C | D |
  | - | - | - | - |
  | 0 | 1 | 0 | a |
  | 3 | 4 | 5 | b |
  | 5 | 5 |   | c |
  | 6 |   |   |   |


</pre>
## csv_correlation.py
<pre>
usage: csv_correlation.py [-h] [-v] [--mode {auto,cross,partial}]
                          [--nlags INT] [--sampling INT] [--na_value FLOAT]
                          [--output FILE]
                          CSV_FILE COLUMN[,COLUMN...]

evaluate cross/auto correlation between columns

positional arguments:
  CSV_FILE              files to read, if empty, stdin is used
  COLUMN[,COLUMN...]    columns to do

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --mode {auto,cross,partial}
                        correlation mode
  --nlags INT           maximum number of lags,default=100
  --sampling INT        number of step for rows to do sample
  --na_value FLOAT      value to fill for NaN,default=0
  --output FILE         path of outut file, default=stdout

remark:
  In results, prefix 'ac_' means result of auto-correlation, prefix 'cc_' means result of cross-correlation.
  prefix 'ac_ci_l' and 'ac_cf_u' mean lower adn upper level of 95% confidence interval for no-correlation.

  For '--mode=cross', nlags means number of records in output. If you want all records from cross-correlation, set nlags=0.

example:
  csv_correlation.py test_correlation.csv COL_0000,COL_0001
  csv_correlation.py test_correlation.csv COL_0000|head|csvlook -I
| index | ac_COL_0000            | ac_ci_l_COL_0000     | ac_ci_u_COL_0000    |
| ----- | ---------------------- | -------------------- | ------------------- |
| 0     | 1.0                    | 1.0                  | 1.0                 |
| 1     | 0.07018334701195321    | -0.06840703542301456 | 0.20877372944692096 |
| 2     | -0.031686282848955645  | -0.17095764718861142 | 0.10758508149070015 |
| 3     | 0.06474599533914761    | -0.07466376744626992 | 0.20415575812456516 |
| 4     | -0.07187457627030945   | -0.21186070987120875 | 0.06811155733058984 |
| 5     | -0.0032344642148376297 | -0.14392762546855406 | 0.13745869703887878 |
| 6     | -0.02065593286982406   | -0.16135052234546393 | 0.12003865660581581 |
| 7     | 0.03586195035334148    | -0.10489087472112046 | 0.1766147754278034  |
| 8     | 0.05144023922871804    | -0.08948797647058224 | 0.19236845492801832 |

  csv_correlation.py --mode=cross test_correlation.csv COL_0000,COL_0001,COL_0002
  csv_correlation.py --mode=cross --sampling=2 test_correlation.csv COL_0000,COL_0001,COL_0002|head|csvlook -I
| index | cc_COL_0000_COL_0001  | cc_COL_0000_COL_0002  | cc_COL_0001_COL_0002  |
| ----- | --------------------- | --------------------- | --------------------- |
| 0     | -0.07832200979116527  | -0.0361744688777645   | -0.0383920692904824   |
| 1     | -0.0584437912103411   | 0.02924305243353182   | 0.0014283173939956392 |
| 2     | -0.004634262357976521 | 0.009863911035045745  | 0.0700311412765593    |
| 3     | 0.08549028836897214   | 0.145849764523322     | -0.07607057576313002  |
| 4     | 0.06411213630824009   | -0.009025766566690439 | -0.043516364265988865 |
| 5     | 0.053392718054984536  | -0.04056558651200204  | 0.09684720026396708   |
| 6     | -0.10900425075345083  | -0.022320478554022246 | 0.0459223360399405    |
| 7     | 0.014787564430673562  | -0.02152087172311092  | -0.00444335370431942  |
| 8     | -0.02779304465519147  | -0.027346286491568755 | 0.12710493528359032   |


</pre>
## csv_crosstable.py
<pre>
usage: csv_crosstable.py [-h] [-v] [--values COLUMN]
                         [--aggregator {sum,min,max,mean,median,prod,count_nonzero}]
                         [--row_names NAME[,NAME...]]
                         [--column_names NAME[,NAME...]]
                         [--normalize {all,index,column}]
                         [--suppress_all_zero] [--output_file FILE]
                         CSV_FILE ROW_COLUMN[,ROW_COLUMN...]
                         COLUMN[,COLUMN...]

make cross-matching table from csv file

positional arguments:
  CSV_FILE              files to read, if empty, stdin is used
  ROW_COLUMN[,ROW_COLUMN...]
  COLUMN[,COLUMN...]

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --values COLUMN       name of column for value
  --aggregator {sum,min,max,mean,median,prod,count_nonzero}
                        aggregator function for '--values', default='sum'
  --row_names NAME[,NAME...]
                        names of rows in output,default=names of given rows
  --column_names NAME[,NAME...]
                        names of columns in output,default=names of given
                        columns
  --normalize {all,index,column}
                        normalized mode, see 'remark'
  --suppress_all_zero   suppress outputing columns whose elements are all NaN
  --output_file FILE    path of output file,default=stdout

remark:

  For '--normalize', following are available.
   ‘all’     : normalize over all values.
   ‘index’   : normalize over each row.
   ‘columns’ : normalize over each column.
  see 'pandas.crosstab https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.crosstab.html'

example:

# input data for example
cat test_crosstable.csv|csvlook -I
| COL001 | COL002 | COL003 | COL004 | COL005 |
| ------ | ------ | ------ | ------ | ------ |
| A      | a      | 1      | 2      | Z      |
| B      | b      | 1      | 3      | X      |
| C      | c      | 1      | 4      | Y      |
| D      | d      | 1      | 5      | Z      |
| A      | b      | 1      | 6      | V      |
| B      | c      | 1      | 7      | W      |
| C      | d      | 1      | 8      | S      |
| D      | a      | 1      | 9      | T      |

csv_crosstable.py test_crosstable.csv COL001 COL002|csvlook -I
| COL001 | a | b | c | d |
| ------ | - | - | - | - |
| A      | 1 | 1 | 0 | 0 |
| B      | 0 | 1 | 1 | 0 |
| C      | 0 | 0 | 1 | 1 |
| D      | 1 | 0 | 0 | 1 |

csv_crosstable.py test_crosstable.csv --values=COL004 COL001 COL002|csvlook -I
| COL001 | a   | b   | c   | d   |
| ------ | --- | --- | --- | --- |
| A      | 2.0 | 6.0 |     |     |
| B      |     | 3.0 | 7.0 |     |
| C      |     |     | 4.0 | 8.0 |
| D      | 9.0 |     |     | 5.0 |

csv_crosstable.py test_crosstable.csv --values=COL004 --aggregator=prod COL001 COL002,COL005
COL002,a,a,a,a,a,a,a,b,b,b,b,b,b,b,c,c,c,c,c,c,c,d,d,d,d,d,d,d
COL005,S,T,V,W,X,Y,Z,S,T,V,W,X,Y,Z,S,T,V,W,X,Y,Z,S,T,V,W,X,Y,Z
COL001,,,,,,,,,,,,,,,,,,,,,,,,,,,,
A,,,,,,,2.0,,,6.0,,,,,,,,,,,,,,,,,,
B,,,,,,,,,,,,3.0,,,,,,7.0,,,,,,,,,,
C,,,,,,,,,,,,,,,,,,,,4.0,,8.0,,,,,,
D,,9.0,,,,,,,,,,,,,,,,,,,,,,,,,,5.0

# with '--suppress_all_zero'
csv_crosstable.py test_crosstable.csv --values=COL004 --aggregator=prod --suppress_all_zero COL001 COL002,COL005
COL002,a,a,b,b,c,c,d,d
COL005,T,Z,V,X,W,Y,S,Z
COL001,,,,,,,,
A,,2.0,6.0,,,,,
B,,,,3.0,7.0,,,
C,,,,,,4.0,8.0,
D,9.0,,,,,,,5.0


</pre>
## csv_dummy.py
<pre>
usage: csv_dummy.py [-h] [-v] [--output FILE] [--quote]
                    [--mode {rand,int,hex,header,arbitrarily}]
                    [--headers FILE]
                    ROWS [COLS]

generate dummy data of csv

positional arguments:
  ROWS                  number of data rows
  COLS                  number of columns

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --output FILE         output file
  --quote               quoteing value of each cell
  --mode {rand,int,hex,header,arbitrarily}
                        value mode of each cell: hex={ir:04x}{ic:04x},
                        rand=random, ind=continus integer, header=definition
                        in headers file
  --headers FILE        list file that has names of columns: csv format as one
                        records or each name per line

remark:
  when '--mode=header' was given, you can use 'np.random.*'. 
  see "Random Generator  NumPy v1.19 Manual https://numpy.org/doc/stable/reference/random/generator.html"

  In header mode, 
  'index' means serial number with 0-base, 'int' means ic+ncols+ir, 
  'rand' means uniform random number in [0,1], 'random.*' means using function in np.random.*,.
  'datetime' means time string of now()+(ir+ic) seconds or frequentry time string with 'datetime:<time string>[:<frequency>]', '<frequency>' is optional.
  '<time string>' is formatted with '%Y-%m-%d %H:%M:%S'. Note: ':' must be esacped by back-slash, see exmple.
  about '<frequency>', see ' pandas documentation https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases'
  'fixed' means fixed value, 
  'list' means random choiced value in list or dictionary with given probabilites.
  'format' means formatted string with 'row', 'col', 'time', 'random' variables, where 'time' is current time(%H%M%S) and 'random' is randomized integer in [0,100].

example:
  csv_dummy.py --mode header --headers bit-pattern-headers.txt 200 > bit-pattern-headers.csv
  csv_dummy.py --headers=headers.txt --mode=header 5 
ABC000,ABC001,ABC002,ABC003,ABC004,ABC005,ABC006,ABC007,ABC008,ABC009,ABC010
0,1,2020-11-01 09:48:38,2020-12-01 08:05:10,ABCDEF,"A0001",0.9769355181667144,"00000007",file_000_008_068_094836.txt,A0001,13
1,16,2020-11-01 09:48:39,2020-12-01 13:05:10,ABCDEF,"A0001",0.9537397926065723,"00010007",file_001_008_043_094836.txt,B0010,13
2,31,2020-11-01 09:48:40,2020-12-01 18:05:10,ABCDEF,"A0001",0.6544350953595085,"00020007",file_002_008_003_094836.txt,B0010,5
3,46,2020-11-01 09:48:41,2020-12-01 23:05:10,ABCDEF,"A0001",0.2262489413244111,"00030007",file_003_008_054_094836.txt,B0010,17
4,61,2020-11-01 09:48:42,2020-12-02 04:05:10,ABCDEF,"A0001",0.23743226355108915,"00040007",file_004_008_022_094836.txt,A0001,17

  header.txt example:
  ABC000 index
  ABC001 int
  ABC002 datetime
  ABC003 datetime:2020-12-01 08\:05\:10:5h
  ABC004 fixed: ABCDEF
  ABC005 q:list:["A0001","A0001","A0001","A0001","B0010"]
  ABC006 rand
  ABC007 q:hex
  ABC008 format:"file_{row:03d}_{col:03d}_{random:03d}_{time}.txt"
  ABC009 list:{"A0001":3,"B0010":2}
  ABC010 list:[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]
  ABC011 random.beta(0.2,10.)
  ABC012 random.normal()
  ABC013 random.exponential()
  ABC014


</pre>
## csv_histogram.py
<pre>
usage: csv_histogram.py [-h] [-v] [--nbins INT]
                        [--nbin_modes {square-root,sturges,rice,doane,s_and_s,freedman_diaconis}]
                        [--range LOWER_X,UPPER_X]
                        [--facets COLUMN[,COLUMN...]] [--output FILE]
                        CSV_FILE COLUMN [WEIGHT_COLUMN]

make histogram from csv file

positional arguments:
  CSV_FILE              files to read, if empty, stdin is used
  COLUMN                name of column to make histogram
  WEIGHT_COLUMN         name of column as weight

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --nbins INT           number of bins, default=20
  --nbin_modes {square-root,sturges,rice,doane,s_and_s,freedman_diaconis}
                        method to evaluate number of bins. if given, '--nbins'
                        is ignored.
  --range LOWER_X,UPPER_X
                        range of x
  --facets COLUMN[,COLUMN...]
                        facets
  --output FILE         path of output file

remark:
  '--range' and 'weight_column' are available for only numerical 'column'.

  about '--nbin_mode', see Histogram - Wikipedia https://en.wikipedia.org/wiki/Histogram .
  NOTE 's_and_s' means Shimazaki and Shinomoto's choice.

example:
  csv_histogram.py --nbins=100 --output=- big_sample_arb.csv  COL_0008|less
  csv_histogram.py --nbins=100 --output=- --range=0.5,1.0 big_sample_arb.csv  COL_0008 COL_0033|less
  csv_histogram.py --facets=B,C,D test_hist.csv E
  csv_histogram.py --facets=B,C,D test_hist.csv A


</pre>
## csv_lmfit.py
<pre>
usage: csv_lmfit.py [-h] [-v] [--model_definition MODEL_NAME|JSON]
                    [--xrange X_MIN,X_MAX] [--output_file OUTPUT]
                    [--remove_offset] [--print_parameters]
                    [--print_sample_model] [--list_internal]
                    [CSV_FILE] [COLUMN] [COLUMN]

fitting function to data in csv file

positional arguments:
  CSV_FILE              files to read, if empty, stdin is used
  COLUMN                name of x column
  COLUMN                name of y column

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --model_definition MODEL_NAME|JSON
                        model definition, 'model_name|json string or @json
                        file', see example
  --xrange X_MIN,X_MAX  range of X
  --output_file OUTPUT  path of output file
  --remove_offset       remove dc offset
  --print_parameters    only print paramters
  --print_sample_model  print sample code for model into stdout
  --list_internal       show list of internal models

remark:
  if model name starts with "@", the name was treadted as class of lmfit.model. see '--list_internal'.
  if model name starts with "%", the name was treated as function that was defined internaly. see '--list_internal'.

example:
  csv_lmfit.py --print_sample_model
  csv_lmfit.py --list_internal
  MDL='local_model1|{"a": {"value": 0, "min": -1, "max": 5, "vary": true}, "b": {"value": 1, "min": -3, "max": 3, "vary": true}, "c": {"value": 1, "min": -1, "max": 1, "vary": true}}'
  python3 lmfit_test.py --model_definition="${MDL}" lmfit_sample.csv
  csv_lmfit.py --model_definition="${MDL}" --model_definition="@LorentzianModel" --output=test_result.csv lmfit_sample.csv X Y
  # read parameters from json file  
  csv_lmfit.py --model_definition="%BetaDistributionModel|@lmfit_test_data_beta.json" --output=test_result.csv lmfit_test_data_beta.csv X Y

#-- template for local_model1.py
csv_lmfit.py --print_sample_model lmfit_sample.csv X Y > local_model1.py
# and edit this soure.

#-- lmfit_sample.py for lmfit_sample.csv
# -- DEBUG
import numpy as np
# import matplotlib.pyplot as plt

npts = 150
x_values = np.linspace(-10, 10, npts)
a = 3
b = 2
c = 1
y_values = a * x_values**2 + b * x_values + c

d_df = pd.DataFrame(columns=["X", "Y"])
d_df["X"] = x_values
d_df["Y"] = y_values
d_df.to_csv("lmfit_sample.csv", index=False)
#--


</pre>
## csv_meltpivot.py
<pre>
usage: csv_meltpivot.py [-h] [-v] [--mode {melt,pivot}] [--category_name NAME]
                        [--value_name NAME] [--values COLUMN[,COLUMN...]]
                        [--single_index_columns] [--output FILE]
                        CSV_FILE KEY_COLUMN[,KEY_COLUMN...]
                        [COLUM[,COLUMN...]]

melting or pivoting csv file

positional arguments:
  CSV_FILE              files to read, if empty, stdin is used
  KEY_COLUMN[,KEY_COLUMN...]
                        names of key columns(index columns)
  COLUM[,COLUMN...]     names of value columns

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --mode {melt,pivot}   mode, default=melt
  --category_name NAME  name of column that is stored names of columns
  --value_name NAME     name of column that is stored value of each column
  --values COLUMN[,COLUMN...]
                        value columns for pivot mode
  --single_index_columns
                        single index for columns for pivot mode
  --output FILE         path of output file

remark:
  The columns, that are given by '--values', must have data type of numeric.

  For mode==melt, when 'columns' argument is not given, others than 'key_columns' are used as 'columns'.

  For mode=pivot, np.sum is used as aggregator function.
  'columns' must be given. NaNs in results are filled by 0.
  If without '--values', it is done with assuming all 'values'=1(pandas.get_dummies() si used)
  For '--single_index_columns', the name of first column, that are given as 'columns', is used 
  to make multiindex of columns into a single index for columns.

example:
  csv_meltpivot.py --category_name=Category --value_name=Value bit-pattern-headers.csv ABC002 BIT000,BIT001,BIT003,BIT004 | head
| ABC002              | Category | Value |
| ------------------- | -------- | ----- |
| 2020-12-01 10:10:15 | BIT000   | 0     |
| 2020-12-01 10:10:17 | BIT000   | 1     |
| 2020-12-01 10:10:19 | BIT000   | 0     |
| 2020-12-01 10:10:21 | BIT000   | 0     |
| 2020-12-01 10:10:23 | BIT000   | 0     |
| 2020-12-01 10:10:25 | BIT000   | 1     |
| 2020-12-01 10:10:27 | BIT000   | 0     |
| 2020-12-01 10:10:29 | BIT000   | 0     |

# in 'test.csv' , above results were stored.
  csv_meltpivot.py --mode pivot --value=Value --single_index_columns test.csv ABC002 Category | csvlook -I
| ABC002              | BIT000 | BIT001 | BIT003 | BIT004 |
| ------------------- | ------ | ------ | ------ | ------ |
| 2020-12-01 10:10:15 | 0      | 1      | 0      | 0      |
| 2020-12-01 10:10:17 | 1      | 0      | 1      | 0      |
| 2020-12-01 10:10:19 | 0      | 0      | 0      | 0      |
| 2020-12-01 10:10:21 | 0      | 0      | 1      | 1      |
| 2020-12-01 10:10:23 | 0      | 1      | 0      | 1      |
| 2020-12-01 10:10:25 | 1      | 0      | 0      | 0      |
| 2020-12-01 10:10:27 | 0      | 1      | 0      | 0      |
| 2020-12-01 10:10:29 | 0      | 1      | 1      | 0      |
| 2020-12-01 10:10:31 | 1      | 1      | 1      | 1      |

  csv_meltpivot.py --mode pivot --values=COL003 test_melt_pivot.csv COL001 COL002 | csvlook -I
| COL001 | CAT0 | CAT1 | CAT2 |
| ------ | ---- | ---- | ---- |
| A      | 1    | 0    | 0    |
| B      | 0    | 0    | 0    |
| C      | 0    | 0    | 2    |

 csv_meltpivot.py --mode pivot --values=COL003 --single_index_columns test_melt_pivot.csv COL001 COL002 | csv_meltpivot.py - COL001| csvlook -I
| COL001 | Category | Value |
| ------ | -------- | ----- |
| A      | CAT1     | 0     |
| B      | CAT1     | 0     |
| C      | CAT1     | 0     |
| A      | CAT0     | 1     |
| B      | CAT0     | 0     |
| C      | CAT0     | 0     |
| A      | CAT2     | 0     |
| B      | CAT2     | 0     |
| C      | CAT2     | 2     |

  csv_meltpivot.py --mode pivot test_melt_pivot.csv COL001 COL002|csvlook -I
%Inf:csv_meltpivot: pivoting without values
| COL001 | COL003 | CAT0 | CAT1 | CAT2 |
| ------ | ------ | ---- | ---- | ---- |
| A      | 1      | 1    | 0    | 0    |
| B      | 0      | 0    | 1    | 0    |
| C      | 2      | 0    | 0    | 1    |

  csv_meltpivot.py --mode pivot test_melt_pivot.csv COL001 COL002,COL003|csvlook -I
%Inf:csv_meltpivot: pivoting without values
| COL001 | COL002_CAT0 | COL002_CAT1 | COL002_CAT2 | COL003_0 | COL003_1 | COL003_2 |
| ------ | ----------- | ----------- | ----------- | -------- | -------- | -------- |
| A      | 1           | 0           | 0           | 0        | 1        | 0        |
| B      | 0           | 1           | 0           | 1        | 0        | 0        |
| C      | 0           | 0           | 1           | 0        | 0        | 1        |

# in above example, this data was used.
 cat test_melt_pivot.csv|csvlook -I
| COL001 | COL002 | COL003 |
| ------ | ------ | ------ |
| A      | CAT0   | 1      |
| B      | CAT1   | 0      |
| C      | CAT2   | 2      |


</pre>
## csv_multiindex_columns.py
<pre>
usage: csv_multiindex_columns.py [-h] [-v] [--nrows INT] [--output FILE]
                                 [--to_single] [--only_header]
                                 CSV_FILE

handle multiindex columns csv

positional arguments:
  CSV_FILE       files to read, if empty, stdin is used

optional arguments:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
  --nrows INT    number of rows as header,default=2
  --output FILE  path of output file, default=stdout
  --to_single    convert single header for columns
  --only_header  parse only header rows

remark:

example:

cat test_multiindex_columns.csv
,,C,,,D,,
A,B,X,Y,Z,X,Y,Z
1,2,3,4,5,6,7,8
3,4,5,6,7,8,9,0

csv_multiindex_columns.py test_multiindex_columns.csv
,,C,C,C,D,D,D
A,B,X,Y,Z,X,Y,Z
1,2,3,4,5,6,7,8
3,4,5,6,7,8,9,0

cat test_multiindex_columns.csv
,,E,,,F,G,
,,C,,,D,,
A,B,X,Y,Z,X,Y,Z
1,2,3,4,5,6,7,8
3,4,5,6,7,8,9,0

 csv_multiindex_columns.py --only_header --nrows=3 test_multiindex_columns.csv
,,E,E,E,F,G,G
,,C,C,C,D,D,D
A,B,X,Y,Z,X,Y,Z
1,2,3,4,5,6,7,8

csv_multiindex_columns.py --nrows=3 --to_single test_multiindex_columns.csv |csvlook -I
| A | B | E_C_X | E_C_Y | E_C_Z | F_D_X | G_D_Y | G_D_Z |
| - | - | ----- | ----- | ----- | ----- | ----- | ----- |
| 1 | 2 | 3     | 4     | 5     | 6     | 7     | 8     |
| 3 | 4 | 5     | 6     | 7     | 8     | 9     | 0     |


</pre>
## csv_print_html.py
<pre>
usage: csv_print_html.py [-h] [-v] [--title TITLE]
                         [--columns COLUMNS[,COLUMNS...]] [--fp_precision INT]
                         [--trim_null STRING=all or ROW:ROW,COL:COL)]
                         [--highlight FLOAT[=(all or ROW:ROW,COL:COL)]]
                         [--min_in_column (all or ROW:ROW,COL:COL)]
                         [--max_in_column (all or ROW:ROW,COL:COL)]
                         [--min_in_row (all or ROW:ROW,COL:COL)]
                         [--max_in_row (all or ROW:ROW,COL:COL)]
                         [--gradient (all or ROW:ROW,COL:COL)]
                         [--bar (all or ROW:ROW,COL:COL]
                         [--max_column_width WIDTH]
                         [--column_width COLUMN:WIDTH[,COLUMN:WIDTH..]]
                         [--part_color STRING:COLOR[,STRING:COLOR...]]
                         [--search_on_html] [--datatable] [--output_file FILE]
                         [--minify]
                         CSV_FILE

print html table made of csv with estimation

positional arguments:
  CSV_FILE              files to read, if empty, stdin is used

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --title TITLE         Title of table
  --columns COLUMNS[,COLUMNS...]
                        names of columns to do
  --fp_precision INT    precision of float, default=2
  --trim_null STRING=(all or ROW:ROW,COL:COL)
                        triming null value
  --highlight FLOAT[=(all or ROW:ROW,COL:COL)]
                        highlighting more than threshold
  --min_in_column (all or ROW:ROW,COL:COL)
                        highlighting minimum cell in each column
  --max_in_column (all or ROW:ROW,COL:COL)
                        highlighting maximum cell in each column
  --min_in_row (all or ROW:ROW,COL:COL)
                        highlighting minimum cell in each row
  --max_in_row (all or ROW:ROW,COL:COL)
                        highlighting maximum cell in each row
  --gradient (all or ROW:ROW,COL:COL)
                        gradient mode
  --bar (all or ROW:ROW,COL:COL)
                        histogram of each column
  --max_column_width WIDTH
                        maximum width of all columns, default='200pm'
  --column_width COLUMN:WIDTH[,COLUMN:WIDTH..]
                        widths of columns
  --part_color STRING:COLOR[,STRING:COLOR...]
                        part color for string, color code is one in css codes.
  --search_on_html      searching on html is enable
  --datatable           datatble mode
  --output_file FILE    path of output file
  --minify              minifing html

remark:
  Elements in only columns, that has int64/float64 as dtype, will be processed.
  So in the following, "8" in Row=4,Col=D is not evaluated for 'max'/'min' and so on.
    | A | B | C | D |
    | - | - | - | - |
    | 1 | 0 | 1 | a |
    | 2 | 2 | 0 | b |
    | 3 |   | 3 |   |
    |   |   | 4 | d |
    | 4 | 6 | 7 | 8 |

  When '--bar' is used, others than '--trim_null' are not available.

  For '--part_color', is you want to use comma(,) an colon(:) in word, then those must be escaped by "".

  NOTE:NOW, '--max_column_width' is not available.

example:
  csv_print_html.py --highlight=2 --gradient=all --max_in_col=all --min_in_col=all t1.csv > test.html
  csv_print_html.py --bar=all --trim_null="-"=all t1.csv > test.html
  csv_print_html.py --min_in_col=0:1 t1.csv > test.html
  csv_print_html.py --min_in_col=,A:B t1.csv > test.html
  csv_print_html.py --highlight=2 --title=HightLight=2 t1.csv > test.html
  csv_print_html.py --bar=all --trim_null="-"=all --columns=A,B,C t1.csv > test.html
  csv_print_html.py --min_in_row=all t1.csv > test.html
  csv_print_html.py --part_color="Joseph:red,Beesley\, Mr. Lawrence:blue" titanic.csv > test.html
  csv_print_html.py --part_color='Joseph:red,Beesley\, Mr. Lawrence:blue,female:green,C\d+:black' titanic.csv > test.html
  csv_print_html.py --part_color='Joseph:red,Beesley\, Mr. Lawrence:blue,female:green,C\d+:black' --column_width="Name:128px" titanic.csv > test.html


</pre>
## csv_print_html_oia.py
<pre>
usage: csv_print_html_oia.py [-h] [-v] [--title TITLE]
                             [--columns COLUMNS[,COLUMNS...]]
                             [--part_color STRING:COLOR[,STRING:COLOR...]]
                             [--search_on_html] [--output_file FILE]
                             [--minify]
                             CSV_FILE COLUMNS [COLUMNS ...]

print html table made of csv with estimation

positional arguments:
  CSV_FILE              file to read, if empty, stdin is used
  COLUMNS               colum names of Observation/Investigation/Action

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --title TITLE         Title of table
  --columns COLUMNS[,COLUMNS...]
                        names of addtional columns
  --part_color STRING:COLOR[,STRING:COLOR...]
                        part color for string, color code is one in css codes.
  --search_on_html      searching on html is enable
  --output_file FILE    path of output file
  --minify              minifing html

remark:

  For '--part_color', is you want to use comma(,) an colon(:) in word, then those must be escaped by "".

example:
  cat test3.csv
IDX,B,C,O,I,A
1,A,Sample1,Observation1:this is a pen,Investigation1:Atre you there?,Action1: nothing to do
2,B,Sample2,Observation2:this is a pen,Investigation2:Atre you there?,Action2: nothing to do
3,C,Sample3,Observation3:this is a pen,Investigation2:Atre you there?,Action3: nothing to do

  csv_print_html_oia.py --columns=IDX,B,C --part_color='this:red' test3.csv  O I A > test.html
  csv_print_html_oia.py --columns=IDX,B,C --part_color='バリ島:red,米国:green,潜水艦:blue,海軍:black' --search_on_html test3.csv  O I A > test.html


</pre>
## csv_print_html_tl.py
<pre>
usage: csv_print_html_tl.py [-h] [-v] [--title TITLE]
                            [--datetime_format FORMAT] [--group_column COLUMN]
                            [--headline_column COLUMN]
                            [--columns COLUMNS[,COLUMNS...]]
                            [--part_color STRING:COLOR[,STRING:COLOR...]]
                            [--group_by_part_color] [--media COLUMN[:COLUMN]]
                            [--cdn] [--output_file FILE] [--minify]
                            CSV_FILE COLUMN_OF_DATETIME COLUMN [COLUMN ...]

print html table made of csv with estimation

positional arguments:
  CSV_FILE              file to read, if empty, stdin is used
  COLUMN_OF_DATETIME    name of column of datetime
  COLUMN                colum names of Observation/Investigation/Action

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --title TITLE         title and description
  --datetime_format FORMAT
                        format string for column of datetime,default=%Y-%m-%d
                        %H:%M:%S
  --group_column COLUMN
                        names of column to make group
  --headline_column COLUMN
                        names of column for short text
  --columns COLUMNS[,COLUMNS...]
                        names of addtional columns
  --part_color STRING:COLOR[,STRING:COLOR...]
                        part color for string, color code is one in css codes.
  --group_by_part_color
                        grouping by result of part_color
  --media COLUMN[:COLUMN]
                        columns for medias
  --cdn                 using CDN(cdn.knightlab.com), default=local
  --output_file FILE    path of output file
  --minify              minifing html

remark:

  Generated html uses script of TimelineJS3. if you used CDN(cdn.knightlab.com), use '--cdn'.
  Without '--cdn', those scripts must be gotten from 'cdn.knightlab.com' and 
  those scripts must be stored in 'timeline3' directory in the same directory as html.
  see "Loading Files Locally" section in Timeline https://timeline.knightlab.com/docs/instantiate-a-timeline.html .

  For '--part_color', is you want to use comma(,) an colon(:) in word, then those must be escaped by "".
  Using '--group_by_part_color', words in '--part_color' are used as group of event.
  when '--part_color' is used, also gantt chart for plantUML will be created. 
  then value of column('--headingline_column') will be used as task name.

  about '--media':
  TimelineJS3 has function to show media(image,vide,etc) for each event.
  using '--media' option, this function is enable: 
  path of media file is given by this option. optional column is column that has title string of each media file.

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
  csv_print_html_tl.py --columns=IDX,B,C --part_color='pen:red,action2:blue,observation3:black' --output=test.html --group_column=B --headline_column=B test3.csv DT O I A
  csv_print_html_tl.py --columns=IDX,B,C --part_color='pen:red,action2:blue,observation3:black' --output=test.html --group_column=B --headline_column=B --title="Title
description" test3.csv DT O I A
  csv_print_html_tl.py --columns=IDX,B,C --part_color='pen:red,action2:blue,observation3:black' --output=test.html --group_by_part_color --headline_column=B --title="Title\ndescription" test3.csv DT O I A
  csv_print_html_tl.py --columns=IDX,B,C --part_color='pen:red,action2:blue,observation3:black' --output=test.html --group_by_part_color --headline_column=B --media=image:title_of_image --title="Title
description" test3.csv DT O I A


</pre>
## csv_query.py
<pre>
usage: csv_query.py [-h] [-v] [--encoding STR] [--query_file FILE]
                    [--columns COLUMNS[,COLUMNS,[COLUMNS,...]]] [--output STR]
                    CSV_FILE [STR]

do query for CSV data

positional arguments:
  CSV_FILE              path of csv file
  STR                   query string

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --encoding STR        encoding, default=utf-8
  --query_file FILE     path of query file
  --columns COLUMNS[,COLUMNS,[COLUMNS,...]]
                        names of colunmns to ouput, default=all
  --output STR          path of output, default is stdout

remark:
 for encoding, see "Codec registry and base classes https://docs.python.org/3/library/codecs.html#standard-encodings"
 you can use str.contains(),str.endswith(),str.startswith(),str.match() and 'in' in query string.

 When '--query_file' was used, those lines were used as query string as joining with 'or'.
 In query file, lines those starts with '#' are ignored as comment lines.

example:
 csv_query.py big_sample_arb.csv 'COL_0002=="001001" and COL_0006=="PAT001"'
 csv_query.py big_sample_arb.csv 'COL_0002=="001001" and COL_0006.str.contains("PAT001")'
 csv_query.py --query_file=test_query.txt test1.csv

 cat test_query.txt
 # test
 B==2
 C==6


</pre>
## csv_sample.py
<pre>
usage: csv_sample.py [-h] [-v] [--range START,END] [--random] [--skip INT]
                     [--output FILE]
                     CSV_FILE SAMPLE_SIZE

derive sample records from big csv file

positional arguments:
  CSV_FILE           files to read, if empty, stdin is used
  SAMPLE_SIZE        size of sample: ex 100 50% 0.5

optional arguments:
  -h, --help         show this help message and exit
  -v, --version      show program's version number and exit
  --range START,END  range for sampling: [0,1.0]
  --random           random sampling
  --skip INT         skip sampling
  --output FILE      path of output file: default=stdout

example:
  csv_sample.py --random --range=0.25,0.75 --output=test.csv big_sample_arb.csv 300


</pre>
## csv_stack_trime.py
<pre>
usage: csv_stack_trime.py [-h] [-v] [--include COLUMNS[,COLUMNS...]]
                          --definition OLD_COL:NEW_COL:APPEND_COL=VALUE[:...]
                          [--columns COL1,COL2,...] [--output FILE]
                          CSV_FILE

split one column, that has multiple meaning, into some columns

positional arguments:
  CSV_FILE              files to read, if empty, stdin is used

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --include COLUMNS[,COLUMNS...]
                        included columns, with csv format
  --definition OLD_COL:NEW_COL:APPEND_COL=VALUE[:...]
                        definition string to make translation
  --columns COL1,COL2,...
                        list of columns at output
  --output FILE         path of output file

remark:
  columns definitions
      old_column_name:new_column_name:append_column=fixed_value:append_column_name=fixed_value....
  the appended_column may be used as a category that was derived from the old_colun_name as one of some meanings,
  and may be used as facet or category of csv_plot_*.

  If argument of '--definition' or '--columns' was started with '@', then those are read from the file.

  if a fixed_value starts with '@', then the remained value without '@' was treated as a column name, 
  so the appended column has the copy of the column, that may mean an attribute column that was BINDED to the old_column_name.
    ex. Cat1_Attr,Cat2_Attr,Attribute,Catgeory1_value,Category2_value 
        => Category1_value:value:Category=1:Attr=@Cat1_Attr,Category2_value:value:Category=2:Attr=@Cat2_Attr

  if more new_columns were given simulitaneously, there will be NaN in each others(see example).

example1:
  csv_stack_trime.py --definition=P1C1:C1:P=P1,P1C2:C2:P=P1,P2C1:C1:P=P2,P2C2:C2:P=P2 --include=N --output=- test3.csv

  input:
  P1C1,P1C2,P2C1,P2C2,N
  1,0,1,0,A
  1,0,0,1,B
  1,0,1,0,C
  1,0,1,0,D

  output:
  C1,C2,N,P
  1,,A,P1
  1,,B,P1
  1,,C,P1
  1,,D,P1
  ,0,A,P1
  ,0,B,P1
  ,0,C,P1
  ,0,D,P1
  1,,A,P2
  0,,B,P2
  1,,C,P2
  1,,D,P2
  ,0,A,P2
  ,1,B,P2
  ,0,C,P2
  ,0,D,P2

example2:
  sv_stack_trime.py --definition=@csv_stack_trim_defs.txt --include=COL3,COL4 csv_stack_trime.csv
  col_defs="COL1:NEW_COL1:COLA=ABC:COLB=CDEF,COL2:NEW_COL2:COLA=ZXY:COLC=1234:COLD=@COL7"
  inc_cols="COL3,COL4"
  csv_stack_trime.py --definition=${col_defs} --include=${inc_cols} csv_stack_trime.csv | csvlook -I

  input:
  COL1,COL2,COL3,COL4,COL5,COL6,COL7
  1,2,3,4,5,6,A
  7,8,9,10,11,12,B
  13,14,15,16,17,18,C
  19,20,21,22,23,24,D

  output:
  | COL3 | COL4 | COLA | COLB | COLC | COLD | NEW_COL1 | NEW_COL2 |
  | ---- | ---- | ---- | ---- | ---- | ---- | -------- | -------- |
  | 3.0  | 4.0  | ABC  | CDEF |      |      | 1        |          |
  | 9.0  | 10.0 | ABC  | CDEF |      |      | 7        |          |
  | 15.0 | 16.0 | ABC  | CDEF |      |      | 13       |          |
  | 21.0 | 22.0 | ABC  | CDEF |      |      | 19       |          |
  | 3.0  | 4.0  | ZXY  |      | 1234 | A    |          | 2        |
  | 9.0  | 10.0 | ZXY  |      | 1234 | B    |          | 8        |
  | 15.0 | 16.0 | ZXY  |      | 1234 | C    |          | 14       |
  | 21.0 | 22.0 | ZXY  |      | 1234 | D    |          | 20       |


</pre>
## csv_status.py
<pre>
usage: csv_status.py [-h] [-v] [--columns COLUMNS]
                     [--mode {count,sum,avg,std,min,max,mode,median,rank,sem,skew,var,mad,kurt,quantile25,quantile50,quantile75,nunique,cumsum,cumprod,vrange,notzero,zero,morethan,lessthan,positive,negative}]
                     [--group COLUMN] [--arguments ARG[,ARG...]]
                     [--output FILE]
                     CSV_FILE

to derive statitical information for each columns

positional arguments:
  CSV_FILE              files to read, if empty, stdin is used

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --columns COLUMNS     name or index of columns as csv format
  --mode {count,sum,avg,std,min,max,mode,median,rank,sem,skew,var,mad,kurt,quantile25,quantile50,quantile75,nunique,cumsum,cumprod,vrange,notzero,zero,morethan,lessthan,positive,negative}
                        name of columns to make group
  --group COLUMN        name of columns to make group with '--mode'
  --arguments ARG[,ARG...]
                        arguments for some mode
  --output FILE         path of output csv file, default=stdout

remark:
  For '--mode', there are results for only columns that have numerical values.
  For '--mode mode', there is result that has 2D data, and if items that have the same count, there are more rows than one in result.

  With '--group', each histogram is made of value grouped by given group column.  

  description of mode:
    count :Count non-NA cells for each column
    sum   :Return the sum of the values for index
    avg   :Return the mean of index
    std   :Return sample standard deviation over index
    min   :Return the minimum of the values for index
    max   :Return the maximum of the values for index
    mode  :without '--group': Get the mode(s) of each element along index
    median:Return the median of the values for index
    rank  :Compute numerical data ranks (1 through n) along index
    sem   :Return unbiased standard error of the mean over index
    skew  :Return unbiased skew over index
    var   :Return unbiased variance over index
    mad   :without '--group':Return the mean absolute deviation of the values for index
    kurt  :without '--group': Return unbiased kurtosis over index
    quantile25:Return values at the given quantile over(=25%)
    quantile50:Return values at the given quantile over(=50%)=median
    quantile75:Return values at the given quantile over(=75%)
    nunique:Count distinct observations over index
    cumsum:Return cumulative sum over index
    cumprod:Return cumulative product over index
    vrange:Return range of value(max-min)
    notzero:Count not zero elements over index
    zero  :Count zero elements over index
    morethan:Coount elements over index, that have more than given value
    lessthan:Coount elements over index, that have less than given value
    positive:Coount elements over index, that have more than 0
    negative:Coount elements over index, that have less than 0

example:
  csv_status.py --mode morethan --arguments=3740 bit-pattern-headers.csv
  csv_uty.py --change_timefreq='D=ABC002:%Y-%m-%d %H\:%M\:%S:floor:10s' bit-pattern-headers.csv|\
     csv_status.py --mode sum --group D -|csv_uty.py --drop_columns=ABC000,ABC001 - |\
     csv_trimtime.py --stack=D - |csv_plot_bar.py --output=test.html --animation_column=D - category stacked_result

  csv_status.py --columns=2,5 big_sample_headers.csv
  == information for columns: ABC001
  count    1116.000000
  mean     4461.000000
  std      2578.446044
  min         1.000000
  25%      2231.000000
  50%      4461.000000
  75%      6691.000000
  max      8921.000000
  Name: ABC001, dtype: float64

  == information for columns: ABC004
  count      1116
  unique        2
  top       A0001
  freq        897
  Name: ABC004, dtype: object
  unique values:
  ('A0001', 897)
  ('B0010', 219)


</pre>
## csv_trim_header.py
<pre>
usage: csv_trim_header.py [-h] [-v] [--rows INT] [--add_column_index] CSV_FILE

DEPRICATED:for csv file, to derive column names in one row from ones in multi rows

positional arguments:
  CSV_FILE            files to read, if empty, stdin is used

optional arguments:
  -h, --help          show this help message and exit
  -v, --version       show program's version number and exit
  --rows INT          number of header rows: default=1
  --add_column_index  add index to column name

remark:
  this script was deprectaed. use 'csv_multiindex_columns.py'.

example:

  csv_trim_header.py --rows=2 test_trim_header.csv
A1_B1,A1_B2,A2_B3,A2_B4,A3_B5,A3_B6,A3_B7,A3_B8

  csv_trim_header.py --rows=2 --add_column_index test_trim_header.csv
A1_B1_00000,A1_B2_00001,A2_B3_00002,A2_B4_00003,A3_B5_00004,A3_B6_00005,A3_B7_00006,A3_B8_00007

cat test_trim_header.csv
A1,,A2,,A3,,
B1,B2,B3,B4,B5,B6,B7,B8


</pre>
## csv_trimtime.py
<pre>
usage: csv_trimtime.py [-h] [-v]
                       [--get_range_of_time COLUMN[:datetime_format]:unit]
                       [--sort_datetime COLUMN_NAME:datetime_format]
                       [--timestamp COLUMN_1:COLUMN_0]
                       [--add_time_column COLUMN:start:freq]
                       [--reformat COLUMN:in_format[:out_format]]
                       [--gap COLUMN=definition[,COLUMN=definition...]]
                       [--time_gap COLUMN=definition[,COLUMN=definition...]]
                       [--calculate_time_diff COLUMN=definition]
                       [--calculate_elapsed_time COLUMN:definition]
                       [--change_timefreq COLUMN=definition[,COLUMN=definition...]]
                       [--resample COLUMN[:time_format]:freq:COLUMN_TO_RESAMPLE[,COLUMN...]]
                       [--resample_function {nearest,count,sum,min,max,mean,std,linear,quadratic,cubic,spline,barycentric,polynomial,krogh,piecewise_polynomial,pchip,akima,cubicspline}]
                       [--select_hours COLUMN[:time_format]:start_time,end_time]
                       [--select_datetime COLUMN[:time_format]:start_time,end_time]
                       [--output FILE]
                       CSV_FILE

triming columns that have time data

positional arguments:
  CSV_FILE              files to read, if empty, stdin is used

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --get_range_of_time COLUMN[:datetime_format]:unit
                        range of time of column, available unit:H,M,S if you
                        use comma or colon in expression, those must be
                        escaped with back-slash
  --sort_datetime COLUMN_NAME:datetime_format
                        sort datetime, format of
                        definition=column_name[:datetime_format].default
                        datetime_format='%Y-%m-%d %H:%M:%S'. if you use comma
                        or colon in expression, those must be escaped with
                        back-slash
  --timestamp COLUMN_1:COLUMN_0
                        convert date time column(COLUMN_0) into
                        timestamp(COLUMN_1)
  --add_time_column COLUMN:start:freq
                        add new column of time series
  --reformat COLUMN:in_format[:out_format]
                        change format of datetime of column if you use comma
                        or colon in expression, those must be escaped with
                        back-slash
  --gap COLUMN=definition[,COLUMN=definition...]
                        group by value gap, format of definitoin is
                        'group_column_name=col_name:gap'. if you use comma or
                        colon in expression, those must be escaped with back-
                        slash
  --time_gap COLUMN=definition[,COLUMN=definition...]
                        group by time gap[seconds],format of definitoin is
                        'group_column_name=col_name:datetime_format:gap'.unit
                        of 'gap' is second. if you use comma or colon in
                        expression, those must be escaped with back-slash
  --calculate_time_diff COLUMN=definition
                        calculate difference[seconds] of datetime
                        column,format of definitoin is
                        'column_name=col_name[:datetime_format[:step]]'.format
                        is datetime format, default='%Y-%m-%d %H:%M:%S'.
                        'step' is integer value, default=1. if you use comma
                        or colon in expression, those must be escaped with
                        back-slash
  --calculate_elapsed_time COLUMN:definition
                        calculate elapsed time[seconds] of datetime
                        column,format of definitoin is 'column_name=col_name[:
                        datetime_format[:origin]]'.format is datetime format,
                        default='%Y-%m-%d %H:%M:%S'. 'origin' is datetime
                        which format is '%Y-%m-%d %H:%M:%S'.if 'origin' was
                        omitted, value at first row will be used as origin. if
                        you use comma or colon in expression, those must be
                        escaped with back-slash
  --change_timefreq COLUMN=definition[,COLUMN=definition...]
                        change datetime frequeny unit:format of definitoin is 
                        'new_column_name=old_col_name:datetime_format:method:f
                        requency'. if you use comma or colon in expression,
                        those must be escaped with back-slash
  --resample COLUMN[:time_format]:freq:COLUMN_TO_RESAMPLE[,COLUMN...]
                        aggregating values of column resampled by time
                        frequency, using function is defined by '--
                        resample_function'
  --resample_function {nearest,count,sum,min,max,mean,std,linear,quadratic,cubic,spline,barycentric,polynomial,krogh,piecewise_polynomial,pchip,akima,cubicspline}
                        aggregation function for '--resample', default=mean
  --select_hours COLUMN[:time_format]:start_time,end_time
                        select hours range, ex: 14:00-18:00 for every days.
                        'start_time' and 'end_time' have the
                        format:%H:%M,%H:%M:%S
  --select_datetime COLUMN[:time_format]:start_time,end_time
                        select datetime range, 'start_time' and 'end_time'
                        have the same format as target column
  --output FILE         path of output csv file, default=stdout

remark:
  # Time series analysis with pandas https://ourcodingclub.github.io/tutorials/pandas-time-series/

  When '--get_range_of_time' was given, only range of time is printed to stdout without other processings.
  Available 'unit' to print is one of 'H'our, 'M'inuts, 'S'econds. See example.

  For '--change_timefreq', available methods are floor, ceil,round. About format string, you may find answer in folowing:
  'datetime  Basic date and time types https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior'.
  About 'freqnecy', you may check the document in following:
  'Time series / date functionality https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases'.

  If you make group according to gap in seriesed values or datetime, '--gap' or '--time_gap' are available.
  This group is useful for plotting by 'csv_plot_*', printing status by 'csv_status'.
  For '--time_gap', about time format string , see above about '--change_timefreq'
  using '--gap', numeric others than date time data are treated.
  For '--gap' and '--time_gap', given gap should be positive.

  If you want to use commas and colon in expression of '--change_timefreq' and others, those must be escaped by back-slash. see examples.

  processing order:
    sort datetime, convert into timestamp, add time column, reformat, gap, time gap, time diff, change timrefreq, resample, 
    select datetime range, select hours range

example:

  csv_trimtime.py --get_range_of_time='A:M' test_trimtime.csv
%inf:csv_uty:get time of range:A:13106.0 mins
  csv_trimtime.py --get_range_of_time='A:M' test_trimtime.csv | sed -E 's/^.*:([0-9.]+) mins//'
13106.0

  csv_trimtime.py --sort_datetime=date a10.csv

  csv_trimtime.py --timestamp="D:A" test_trimtime.csv
  csv_trimtime.py --add_time_column="D:2020-12-01 12\:12\:12:5s" test_trimtime.csv
  csv_trimtime.py --reformat="A:%Y-%m-%d %H\:%M\:%S:%Y/%m/%dT%H\:%M\:%S" test_trimtime.csv
  csv_trimtime.py --gap="GC=C:1" test_trimtime.csv

  csv_trimtime.py --time_gap="GA=A::61" test_trimtime.csv
%Inf:csv_trimtime:groupby time gap
%inf:csv_trimtime:groupby_time_gap:['GA=A::61']
%inf:csv_trimtime:groupby_time_gap:column=GA:number of groups=4:max count in each group=3
A,B,C,GA
2020-11-14 10:00:00,1,19,0
2020-11-13 10:00:00,1,19,1
2020-11-13 10:01:00,2,18,1
2020-11-13 10:02:00,3,7,1

  csv_trimtime.py --change_timefreq='D=ABC002:%Y-%m-%d %H\:%M\:%S\:floor\:30s' big_sample_headers.csv |\
                                                              csv_plot_histogram.py --animation_column=D --output=test.html - ABC005

  # in following example, column 'D' will be created as column of timestamp, and by those dataframe will be made into group and stacked.
  # at plot, the timestamp column 'D' will be used as animation key frames.
  csv_trimtime.py --change_timefreq='D=ABC002:%Y-%m-%d %H\:%M\:%S:floor:10s' bit-pattern-headers.csv|\
     csv_status.py --mode sum --group D -|csv_uty.py --drop_columns=ABC000,ABC001 - |\
     csv_uty.py --stack=D - |csv_plot_bar.py --output=bit-pattern-headers_10sec_sum.html --animation_column=D --yrange=0,1 - category stacked_result

  csv_trimtime.py --resample="A:%Y-%m-%d %H\:%M\:%S:2min:B,C" --resample_func=mean test_trimtime.csv

  csv_trimtime.py --select_hours="A:10\:00\:00,11\:00\:00" test_trimtime.csv
  csv_trimtime.py --select_hours="A:10\:00\:00,1\:00\:00pm" test_trimtime.csv
  csv_trimtime.py --select_datetime="date:%Y-%m-%d:2007-01-01,2007-12-01" a10.csv

  csv_trimtime.py --calculate_time_diff="TD=A:%Y-%m-%d %H\:%M\:%S:1" test_trimtime.csv
A,B,C,TD
2020-11-14 10:00:00,1,19,
2020-11-13 10:00:00,1,19,-86400.0
2020-11-13 10:01:00,2,18,60.0

  csv_trimtime.py --calculate_elapsed_time="G=date:%Y-%m-%d:2007-08-01 00\:00\:00" a10.csv
date,value,G
2007-06-01,20.681002,-5270400.0
2007-07-01,21.834889999999998,-2678400.0
2007-08-01,23.93020353,0.0
2007-09-01,22.93035694,2678400.0
2007-10-01,23.26333992,5270400.0


</pre>
## csv_uty.py
<pre>
usage: csv_uty.py [-h] [-v] [--serial_column COLUMN[:STEP]]
                  [--drop_columns_regex REGEX]
                  [--drop_columns COLUMN[,COLUMN[,COLUMN...]]
                  [--drop_rows INT[,INT]|INT-INT]
                  [--drop_na_columns COLUMN[,COLUMN[,COLUMN...]]
                  [--drop_duplicated COLUMN[,COLUMN[,COLUMN...]]
                  [--prologe CODE;[CODE;CODE;...]]
                  [--change_timefreq COLUMN=definition[,COLUMN=definition...]]
                  [--add_columns COLUMN=expr[,COLUMN=expr...]]
                  [--trim_columns COLUMN=CODE[,COLUMN=CODE[,COLUMN=CODE...]]
                  [--type_columns COLUMN=type[,COLUMN=type..]]
                  [--fillna COLUMN=value[,COLUMN=value...]]
                  [--replace COLUMN=JSON[,COLUMN=JSON...]]
                  [--split_into_rows COLUMN[:SEPARATOR[,COLUMN:SEPARATOR]]]
                  [--split_into_columns COLUMN[:SEPARATOR[,COLUMN:SEPARATOR]]]
                  [--decompose_bit_string COLUMN[:NBITS[,COLUMN...]]]
                  [--rename_columns OLD_NAME:NEW_NAME[,OLD_NAME:NEW_NAME...]]
                  [--sort [sort_order|]COLUMN[,COLUMN...]]
                  [--sort_datetime [sort_order|]COLUMN:FORMAT]
                  [--stack COLUMN] [--transpose]
                  [--output_format {csv,hdf,parquet,pickel,json,feather,stata}]
                  [--columns_regex COLUMN[,COLUMN[,COLUMN...]]
                  [--columns COLUMN[,COLUMN[,COLUMN...]] [--output FILE]
                  CSV_FILE

utility for CSV file

positional arguments:
  CSV_FILE              file to read. if "-", stdin is used

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --serial_column COLUMN[:STEP]
                        add new column that has continus numbers, 0-base. If
                        STEP was given, steped number is used.
  --drop_columns_regex REGEX
                        pattern of column names to drop
  --drop_columns COLUMN[,COLUMN[,COLUMN...]
                        names of columns to drop
  --drop_rows INT[,INT]|INT-INT
                        index of rows to drop, 0-base
  --drop_na_columns COLUMN[,COLUMN[,COLUMN...]
                        names of columns to check NA and to drop. if 'all',
                        rows are dropped with how='any'
  --drop_duplicated COLUMN[,COLUMN[,COLUMN...]
                        names of columns to check duplicated rows and to drop
                        others than first. if 'all', all columns are used to
                        check
  --prologe CODE;[CODE;CODE;...]
                        pieces of python code to pre-load, for use in
                        expression of '--add_columns'.
  --change_timefreq COLUMN=definition[,COLUMN=definition...]
                        [DEPRECATED]change datetime frequeny unit: format of
                        definitoin is 'new_column_name=old_col_name:format:met
                        hod:frequency'. if you use comma or colon in
                        expression, those must be escaped with back-slash
  --add_columns COLUMN=expr[,COLUMN=expr...]
                        names and expressions of columns to add or replace,
                        with csv format. if you use comma in expression, the
                        comma must be escaped with back-slash
  --trim_columns COLUMN=CODE[,COLUMN=CODE[,COLUMN=CODE...]
                        piece of python code for each column to replace and
                        output
  --type_columns COLUMN=type[,COLUMN=type..]
                        data type for each column:type=str, int, float, bin,
                        oct, hex
  --fillna COLUMN=value[,COLUMN=value...]
                        fill na for each column. if starts with '@', internal
                        function will be used, see remark.
  --replace COLUMN=JSON[,COLUMN=JSON...]
                        replace value for each column
  --split_into_rows COLUMN[:SEPARATOR[,COLUMN:SEPARATOR]]
                        split each element value with csv format and store
                        those into rows, default of separator=','
  --split_into_columns COLUMN[:SEPARATOR[,COLUMN:SEPARATOR]]
                        split each element value with flag format and store
                        those into columns, default of separator='|'
  --decompose_bit_string COLUMN[:NBITS[,COLUMN...]]
                        decompose string as bit pattern. ex 01010101
  --rename_columns OLD_NAME:NEW_NAME[,OLD_NAME:NEW_NAME...]
                        rename columns
  --sort [sort_order|]COLUMN[,COLUMN...]
                        sorting for columns, sort_order=ascendig or descendig
  --sort_datetime [sort_order|]COLUMN:FORMAT
                        sorting for columns as datetime, sort_order=ascendig
                        or descendig
  --stack COLUMN        name of column to make group with stacking
  --transpose           transpose dataframe
  --output_format {csv,hdf,parquet,pickel,json,feather,stata}
                        output format
  --columns_regex COLUMN[,COLUMN[,COLUMN...]
                        pattern of column names to output
  --columns COLUMN[,COLUMN[,COLUMN...]
                        names of columns to output
  --output FILE         path of output csv file, default=stdout

remark:
  Process of '--serial_column' is done at first, so the result of '--serial_column' may be used as a coluumn for '--add_columns', others.
  Note: result of '--serial_column' will be affected at proceeding processing for '--drop_na_columns', others.

  All columns are read as "str", so you may convert type of those if need, using '--add_columns', '--trim_columns', '--type_columns'.

  For '--add_column', available name of column is to match with '[\w:;@_；：＠＿]+'.
  At '--add_columns', there are '$' prefix column names in right-side of each defitiion, see examples.

  At '--trim_columns', in right-side of each definition, there is a lambda function, 
  the function will be applied by Series.map, see examples.

  If you want to use commas in expression of '--add_columns' and '--trim_columns', the comma must be escaped by back-slash. see examples.
  For '--add_columns', values of each column, that start with '0b' or '0o' or '0x', are converted int integer internaly,
  but at output value of those columns was formatted back into original format.

  [DEPRECATE] '--change_timefreq' was deprecated. use 'csv_trimtime'.
  For '--change_timefreq', available methods are floor, ceil,round. About format string, you may find answer in
  'datetime  Basic date and time types https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior'.
  About 'freqnecy', you may check the document in 
  'Time series / date functionality https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases'.
  If you want to use commas and colon in expression of '--change_timefreq', those must be escaped by back-slash. see examples.

  After other processings, '--trim_columns' are applied immediately before output.
  When '--drop_dulicated' was given, first row that has same values of columns will be remained.

  For '--decompose_bit_string', new columns are added, names of those has '_Bnnn' as suffix.
  NBITS means minimum number of columns for decomposed results.
  If values has prefix '0b', '0o','0x' or is string of decimal, then the values are decoded into binary string and decomposed.
  And value of elements is treated as bits pattern string. So results have reversed order: 
   ex: COL_A:10011 => [COL_A_B000:"1",COL_A_B001:"1",COL_A_B002:"0",COL_A_B003:"0",COL_A_B004:"1"]
  Note: if there are "100" and "200" in the same column, "100" is treated as binary string "0b100", 
        but "200" is treated as decimal value and results is ["1","1","0","0","1","0","0","0"].

  For '--stack', there are [<column name>,'category','stacked_result'] as columns in header of results. 
  '<column name>' is name given by '--stack'.

  For '--fillna', if '@interpolate' was used as value, NaN are filled by interpolated by linear method with both inside and outside.
  If '@forward' was used as value, propagate last valid observation forward to next valid
  If '@backward' was used as value, use next valid observation to fill gap.

  For '--replace', definition has json format as dict: '{"old_value":"new_value",...}' 
  NOTE: In definition, old value must be string. ex: '{"1":"A"}'
  If you want to use commas in definition of '--replace', those must be escaped by back-slash. see examples.

  If you want to use commas and colon in expression of '--split_into_rows' and '--split_into_columns', 
  those must be escaped by back-slash. see examples.

  For '--split_into_columns', the separactor is sigle character or regexp.
  If named parameter is used, the names are names of columns in the result. see example.

  output format:
    csv      : comma-separated values (csv) file
    hdf      : HDF5 file using HDFStore
    parquet  : the binary parquet format, that reuires pyarrow module
    pickeld  : Pickle (serialize) object to file
    json     : JSON string
    feather  : binary Feather format, that requires pyarrow module
    stata    : Stata dta format

  processing order:
   add serial column, dropping columns(regx), dropping rows, dropping na, dropping duplicated, adding columns that was changed with time frequency, 
   adding columns, triming columns, type columns,filling value for na, replace values, split into rows, split into columns, 
   decompose bits string, sort/sort by datetime, rename columns, stacking

SECURITY WARNING:
  this use 'exec' for '--add_columns' and '--prologe', '--trim_columns' without any sanity.

example:
  csv_uty.py --serial_column=serial:100 test1.csv
  csv_uty.py --drop_columns=A,B --drop_rows=1 test1.csv
  csv_uty.py --drop_na_columns=all test1.csv | csv_uty.py --serial_column=serial:100 -
  csv_uty.py --drop_rows=0-1 test1.csv
  csv_uty.py --drop_na_columns=P1C1,P1C2,P2C1 test3.csv
  csv_uty.py --drop_duplicated=P1C1 test3.csv

  csv_uty.py --add_columns='NCOL1="PAT001",NCOL2=12345,NCOL3=${A}+${B}' test1.csv
  csv_uty.py --add_column='E=(${D}.fillna("0").apply(lambda x: int(x\,2)) & 0b10)' test1.csv
  acol='NCOL1="PAT001",NCOL2=12345,NCOL3=(${D}.fillna("0").apply(lambda x: int(x\,0)) & 0b10)!=0'
  csv_uty.py --add_columns="${acol}" test1.csv
  acol='NCOL1="PAT001",NCOL2=12345,NCOL3=np.sin(${A}.fillna("0").astype(float))'
  csv_uty.py --prologe='import numpy as np;' --add_columns="${acol}" --columns=NCOL1,NCOL2,NCOL3,A,B,C,D test1.csv
  acol='NCOL1=${A}.map(lambda x: format(int(x)\, "#010x")\, na_action="ignore")'
  csv_uty.py --prologe='import numpy as np;' --add_columns="${acol}" --columns=NCOL1,A,B,C,D test1.csv
  # Series  pandas 1.1.3 documentation https://pandas.pydata.org/pandas-docs/stable/reference/series.html#accessors
  csv_uty.py --add_columns='D=${ABC002}.str.replace(r":\d+$"\,":00"\,regex=True)' big_sample_headers.csv |\
                                                              csv_plot_histogram.py --output=test.html --animation_column=D - ABC005
  csv_uty.py --add_columns='D=pd.to_datetime(${ABC002}\,format="%Y-%m-%d %H:%M:%S")' big_sample_headers.csv
  csv_uty.py --add_columns='D=pd.to_datetime(${ABC002}\,format="%Y-%m-%d %H:%M:%S"),E=${D}.dt.floor("30s")' big_sample_headers.csv |\
                                                              csv_plot_histogram.py --animation_column=E --output=test.html - ABC005

  # the same as above
  #[DEPRECATE] '--change_timefreq' was deprecated. use 'csv_trimtime'.
  csv_uty.py --change_timefreq='D=ABC002:%Y-%m-%d %H\:%M\:%S:floor:30s' big_sample_headers.csv |\
                                                              csv_plot_histogram.py --animation_column=D --output=test.html - ABC005

  csv_uty.py --trim_columns=D="lambda x: int(x\,0)" test1.csv # convert binary string into decimal value.
  csv_uty.py --type_columns=A=float,B=bin test2.csv

  csv_uty.py --decompose_bit_string=D:16 test1.csv |csvlook -I
  csv_uty.py --decompose_bit_string=A,B,C,D --rename_columns=A_B000:BIT_A,A_B001:BIT_B test1.csv

  csv_uty.py --rename_columns=A:abc,B:def test1.csv

  csv_uty.py --stack=ABC002 bit-pattern-headers.csv

  csv_uty.py --fillna=A=1,B=2,C="A B" test1.csv
  csv_uty.py --fillna=B=@interpolate test1.csv
  csv_uty.py --fillna=A=@forward t1.csv
  csv_uty.py --fillna=A=@backward t1.csv

  csv_uty.py --replace='A={"1":"A"\,"2":"B"},D={"a":1\,"b":0}' t1.csv

  csv_uty.py --split_into_rows="COL003" test_explode.csv
  csv_uty.py --split_into_rows="COL002:\:,COL003" test_explode.csv
  csv_uty.py --split_into_rows="COL002:\:" test_explode.csv |csvlook -I
  | COL001 | COL002 | COL003 | COL004   |
  | ------ | ------ | ------ | -------- |
  | A      | 1      | 1,2,3  | F1|F2|F3 |
  | A      | 2      | 1,2,3  | F1|F2|F3 |
  | A      | 3      | 1,2,3  | F1|F2|F3 |
  | B      | 2      | 4,5,6  | F2       |
  | C      | 3      | 7,8,9  | F1|F3    |

  csv_uty.py --split_into_columns="COL002:\:,COL004" test_explode.csv|csvlook -I
  | COL001 | COL002 | COL003 | COL004   | 1 | 2 | 3 | F1 | F2 | F3 |
  | ------ | ------ | ------ | -------- | - | - | - | -- | -- | -- |
  | A      | 1:2:3  | 1,2,3  | F1|F2|F3 | 1 | 1 | 1 | 1  | 1  | 1  |
  | B      | 2      | 4,5,6  | F2       | 0 | 1 | 0 | 0  | 1  | 0  |
  | C      | 3      | 7,8,9  | F1|F3    | 0 | 0 | 1 | 1  | 0  | 1  |

  csv_uty.py --split_into_columns="COL002:(?P<alpha>\w+)(?P<D>\d+),COL004" test_explode.csv|csvlook -I
  | COL001 | COL002 | COL003 | COL004   | alpha | D | F1 | F2 | F3 |
  | ------ | ------ | ------ | -------- | ----- | - | -- | -- | -- |
  | A      | 1:2:3  | 1,2,3  | F1|F2|F3 |       |   | 1  | 1  | 1  |
  | B      | AB2    | 4,5,6  | F2       | AB    | 2 | 0  | 1  | 0  |
  | C      | D3     | 7,8,9  | F1|F3    | D     | 3 | 1  | 0  | 1  |

  # in following example, column 'D' will be created as column of timestamp, and by those dataframe will be made into group and stacked.
  # at plot, the timestamp column 'D' will be used as animation key frames.
  # [DEPRECATE] '--change_timefreq' was deprecated. use 'csv_trimtime'.
  csv_uty.py --change_timefreq='D=ABC002:%Y-%m-%d %H\:%M\:%S:floor:10s' bit-pattern-headers.csv|\
     csv_status.py --mode sum --group D -|csv_uty.py --drop_columns=ABC000,ABC001 - |\
     csv_uty.py --stack=D - |csv_plot_bar.py --output=bit-pattern-headers_10sec_sum.html --animation_column=D --yrange=0,1 - category stacked_result

  csv_uty.py --sort=ABC004 test_sort.csv
  csv_uty.py --sort="desc|ABC004,ABC005" test_sort.csv
  csv_uty.py --sort_datetime="ABC002" test_sort.csv
  csv_uty.py --sort_datetime="desc|ABC002" test_sort.csv
  csv_uty.py --sort_datetime="ABC002:%Y-%m-%d %H\:%M\:%S" test_sort.csv

  csv_uty.py --output_format=hdf --output=test.dat bit-pattern-headers.csv

  input: test1.csv
  A,B,C,D
  1,2,3,0b01010
  4,5,6,0b01

  input: test3.csv
  P1C1,P1C2,P2C1,P2C2,N
  1,0,1,0,A
  1,0,0,1,B
  1,0,1,0,C
  1,0,1,0,D
  ,1,1,1,E
  ,,1,1,F
  1,1,,1,G


</pre>
## csv_window_rolling.py
<pre>
usage: csv_window_rolling.py [-h] [-v] [--index COLUMN]
                             [--window_type {boxcar,triang,blackman,hamming,bartlett,parzen,bohman,blackmanharris,nuttall,barthann}]
                             [--window_function {sum,min,max,mean,median,std,count,var,skew,kurt,corr,cov}]
                             [--output_file FILE]
                             CSV_FILE COLUMN[,COLUMN..] INT

do rolling columns data, like as moving-average

positional arguments:
  CSV_FILE              files to read, if empty, stdin is used
  COLUMN[,COLUMN..]     columns to process
  INT                   size of window

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --index COLUMN        column of independent values, default=id of rows
  --window_type {boxcar,triang,blackman,hamming,bartlett,parzen,bohman,blackmanharris,nuttall,barthann}
                        type of window function
  --window_function {sum,min,max,mean,median,std,count,var,skew,kurt,corr,cov}
                        function to do
  --output_file FILE    path of output file, default=stdout

remark:
   If window_type is not None, only one of ["sum", "mean", "var", "std"] is abailable as window_function. 

example:
  csv_window_rolling.py big_sample_rand.csv COL_0000 20
  csv_window_rolling.py --window_type=boxcar --window_function=std big_sample_rand.csv COL_0000 20


</pre>
## csv_write_excel.py
<pre>
usage: csv_write_excel.py [-h] [-v] [--columns COLUMN[,COLUMN...]]
                          [--image_column COLUMN]
                          [--image_output_column COLUMN]
                          [--image_size WIDTH,HEIGHT] [--hyperlink]
                          [--output EXCEL_FILE]
                          CSV_FILE

write csv to ms-excel file with images

positional arguments:
  CSV_FILE              csv file to read

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --columns COLUMN[,COLUMN...]
                        names of columns to write: default=all
  --image_column COLUMN
                        name of column for path of a image file
  --image_output_column COLUMN
                        name of column to insert the image, default='Image'
  --image_size WIDTH,HEIGHT
                        maximum size of image at cell of excel,
                        default='120,120'
  --hyperlink           enable hyperlink for file path or url
  --output EXCEL_FILE   path of file to output

remark:
  The values, except for numerics,  will be treated as string on excel.

  The datetime values in csv file are converted as string into cells of excel.
  So for treating datetime on excel, the value must be converted by '=DATEVALUE()' and appropriate format on excel.

  Using '--hyperlink', a cell will be with a hyperlink attribute for URL with http/https/file protocol or 
  a value of cell that is available as a path of a file.

  you may execute following vba on the excel to set a property of an image object.
How to automatically change all pictures to move and size with cells in Excel? https://www.extendoffice.com/documents/excel/4923-excel-picture-move-and-size-with-cells-default.html
</pre>
##
<pre>
Sub MoveAndSizeWithCells()
    Dim xPic As Picture
    On Error Resume Next
    Application.ScreenUpdating = False
    For Each xPic In ActiveSheet.Pictures
        xPic.Placement = xlMoveAndSize
    Next
    Application.ScreenUpdating = True
End Sub
</pre>
##
<pre>

example:
  csv_write_excel.py --image_column=file_name --output=images.xlsx images.csv
  csv_write_excel.py --image_column=file_name --output=images.xlsx --hyperlink images.csv
</pre>
## csv_cut.sh
<pre>
print range of rows and range of columns in csv file
Usage: csv_cut.sh [-i] csv_file range_of_rows range_of_columns
arguments:
  csv_file        : csv file
  range_of_rows   : range of rows to print with csv format, 1-base
                    alse keyword 'all' is availabe.
                    ex. 10,20 10,+10 all
  range_of_columns: range of columns to print with csv format, 1-base
                    also name of column or 'all' is available.
                    ex. 10,20 10,+10 CO_0000,COL_0002

options:
  -i :add index column

example:
  csv_cut.sh -i big_sample_int.csv 100,+3 1000,+3|csvlook -I
  -- range of rows   : 100-103
  -- range of columns: 1000-1003
  | index | COL_0999 | COL_1000 | COL_1001 | COL_1002 |
  | ----- | -------- | -------- | -------- | -------- |
  | 100   | 111483   | 111484   | 111485   | 111486   |
  | 101   | 112599   | 112600   | 112601   | 112602   |
  | 102   | 113715   | 113716   | 113717   | 113718   |
  | 103   | 114831   | 114832   | 114833   | 114834   |

  csv_cut.sh -i big_sample_int.csv 100,+3 500,+3|csvtool transpose -|csvlook -I
  -- range of rows   : 100-103
  -- range of columns: 500-503
  | index    | 100    | 101    | 102    | 103    |
  | -------- | ------ | ------ | ------ | ------ |
  | COL_0499 | 110983 | 112099 | 113215 | 114331 |
  | COL_0500 | 110984 | 112100 | 113216 | 114332 |
  | COL_0501 | 110985 | 112101 | 113217 | 114333 |
  | COL_0502 | 110986 | 112102 | 113218 | 114334 |


</pre>
## csv_dtype.sh
<pre>
to estimate data type of each column
Usage: csv_dtype.sh [-i] [-c columns] [-r number] [-v] csv_file
arguments:
  csv_file : path of csv file
options:
  -i        : print index of column, 1-base
  -c columns: indexes of columns to parse, 1-base ex.1,3-10
  -r number : number of rows to scan, default=10
  -v        : verbose

example:
  csv_dtype.sh -c 1-100 big_sample_arb.csv | awk '=="binary" {print /home/akei/library/csv_tools/csv_utility/csv_dtype.sh}'
  csv_dtype.sh -i -c 1-20 -v big_sample_arb.csv

remark:
  


</pre>
## csv_dummy.sh
<pre>
make simple dummy record with csv format
Usage: csv_dummy.sh [-q] number_of_data_rows number_of_columns
options:
  -q : quoting cell value.



</pre>
## csv_function.sh
<pre>
replace contents of columns with values that were processed by 'function'.
Usage: csv_function.sh [-a suffix] csv_file columns function_name
Usage: csv_function.sh -l

arguments:
  csv_file      : path of csv file
  columns       : columns to apply function,1-base, ex. 1-2,3 
  function_name : program or npath of shell script or implicit function(see '-l')

options:
  -l: print available implicit function
  -a suffix: append mode, suffix is used for new columnm name.

remark:
  program or script has each value of columns as arguments, 
  and write results with csv format, that has same number of fileds.

  sample of script(bin2dec):
       INS=("${@}")
       RES=""
       BASE=2
       for v in ${INS[@]}; do
           if [[ ${v} =~ [^0-9] ]]; then
	   	RES="${RES}${v},"
           else
	    	RES="${RES}$((${BASE}#${v})),"
           fi
       done

       if [[ ${#RES} == 0 ]]; then
           echo "${INS[@]}"
       else
           RES=${RES::-1}
           echo "${RES}"
       fi

example:
 csv_function.sh test.csv 1 bin2dec

 input:
 A,B
 10,01
 11,10

 output:
 A,B
 2,01
 3,10



</pre>
## csv_get_col_index.sh
<pre>
to get index of column  or name of column with 1-base,
Usage: csv_get_col_index.sh csv_file column_name_or_index



</pre>
## csv_head.sh
<pre>
command like head for csv.
Usage: csv_head.sh [-t] [-c range_of_columns] [-r number_of_rows] csv_file 
options:
  -c range_of_columns: range of columns as 1-base index ex.:16,20-31
  -r numbr_or_rows   : number of rows to view
  -t                 : tail mode
remark:
  as assumption, there is only one header row in csv file.



</pre>
## csv_hist_console.sh
<pre>
plot histogram by ascii character.
Usage: csv_hist_console.sh [-p] [-s] [-d] [-l] csv_file X_column [y_column]
arguments:
  csv_file : path of csv file
  x_column : column index of x, 0-base
  y_column : column index of y, 0-base
options:
  -p      : line plot, y_column is required.
  -s      : scatter plot, y_column is required.
  -d      : heat map plot, y_column is required.
  -l      : histogram, y_column is not required.
  -b bins : number of bins for '-d' and '-l', default=20 

remark:
 at least one of '-p', '-s', '-d', '-l' must be given.
 GitHub - sgreben/jp: dead simple terminal plots from JSON data. single binary, no dependencies. linux, osx, windows. 
  https://github.com/sgreben/jp

example:
   csv_hist_console.sh -l test_plot.csv 1



</pre>
## csv_join.sh
<pre>
join two csv file into one csv file
Usage: csv_join.sh [-m mode] columns_1 csv_file_1 columns_2 csv_file_2
Usage: csv_join.sh -s [-m mode] columns csv_file_1 csv_file_2
options:
  -s     : use same names of columns to join
  -m mode: join mode, l=left, r=right, f=full, default=l

example:
  csv_join.sh A,B test1.csv A,B test2.csv
  csv_join.sh -s A,B test1.csv test2.csv



</pre>
## csv_matrix.sh
<pre>
convert matrix data into (x,y,v).
Usage: csv_matrix.sh [-n] csv_file
options:
  -n : no header mode

remark:
  output file may be used by csv_plot_heatmap.py, and so on.

example1:
  csv_matrix.sh test_matrix.csv |csv_plot_heatmap.py --format=html --side_hist - ROW_ID COL_ID value >test.html

example2:
  csv_matrix.sh test_matrix.csv
input=
,A,B,C,D,E
Z,1,2,3,4,5
Y,6,7,8,9,10

output:
ROW_ID,COL_ID,value
Z,A,1
Z,B,2
Z,C,3
Z,D,4
Z,E,5
Y,A,6
Y,B,7
Y,C,8
Y,D,9



</pre>
## csv_print.sh
<pre>
to print contents around given (row,col) in csv file.
Usage: csv_print.sh [-n] [-c int]  [-r int] csv_file row col
arguments:
  row : index of row, integer
  col : index of column, integer
options:
  -c int: half width of view for columns
  -r int: half width of view for rows
  -n    : row number mode

remark:
  as assumption, there is only one header row in csv file.



</pre>
## csv_print_head.sh
<pre>
to print names of columns in csv file
Usage: csv_print_head.sh [-t] [-c columns] [-n index_width] [-r nrows] csv_file

options:
  -t             : table format
  -c columns     : index of columns to print, ex: 1-10,51-60
  -n index_width : number of width of index, default=5
  -r nrows       : multiindex columns mode, nrows is number of rows of headers

remark:
  as assumption, there is only one header row in csv file.



</pre>
## csv_quick_view.sh
<pre>
Usage: csv_quick_view.sh [-s word] csv_file
options:
  -s word: word to search

remark:
  see folloing
  Pretty CSV viewing on the Command Line - Stefaan Lippens inserts content here https://www.stefaanlippens.net/pretty-csv.html


</pre>
## csv_search_rc.sh
<pre>
to search keyword in csv file and to return the position:(row,col)
Usage: csv_search_rc.sh [-w] [-l] keyword csv_file
arguments:
  keyword : keyword to search, grep regex pattern is available.
  csv_file: csv file

options:
  -l: one result as one line
  -w: keyword as word

remark:
  as assumption, there is only one header row in csv file.



</pre>
## csv_split_columns.sh
<pre>
to split ONE csv file into some csv files, that may have too many columns.
Usage: csv_split_columns.sh [-n limit_columsn] index_column csv_file
arguments:
  index_column : column label that index column has.
                 in all results, there is this column.
                 if number, then as 0-base index number of fields.
options:
  -n limit_columns : maximum number of columns that one csv file has.
                     this limit may be given by limitation of database.
                     default is 2000
remark:
  as assumption, there is only one header row in csv file.

example:
csv_split_columns.sh 0 sample.csv
csv_split_columns.sh ID sample.csv



</pre>
## csv_sqlite_insert.sh
<pre>
inset contents of csv file into sqlitDB
Usage: csv_sqlite_insert.sh [-d db_name] [-s number_of_rows] [-p primary_keys] table_name csv_file
options:
  -d db_name:  name of data base
  -p primary_keys: primary keys, with csv format
  -s number_of_rows: number of scaned rows for creatign table


</pre>
## csv_stack.sh
<pre>
simply append csv files according to columns or rows.
Usage: csv_stack.sh [-m dir] [-c categories] [-r n] csv_file csv_file [csv_file ...]
options:
  -r n          : number of rows of headers, default=1
  -m dir        : direction of stack, v or h, default=v
  -c categories : name of categories for each csv files, with csv format.
                  this options is available for only vertical mode.
remark:
 when '-c' option was used, number of categories must be equal to number of csv files.
 if this option was given, for each record there is column of category in result.

example:
  csv_stack.sh -c p1,p2 test1.csv test2.csv
  A,B,Category
  1,2,p1
  3,4,p1
  5,6,p1
  7,8,p2
  9,10,p2
  11,12,p2
  13,14,p2



</pre>
## csv_status_xsv.sh
<pre>
print status of each column by 'xsv'
Usage: csv_status_xsv.sh [-c columns] [-f number] csv_file
options:
  -c columns: columns to analysis, 1-base, default=all
  -f number : less than this number of freqeuncy, default=(number of records)/10


</pre>
## csv_to_db_csvkit.sh
<pre>
to insret contents of csv file into db by csvkit
Usage: csv_to_db_csvkit.sh [-i] [-d db_name] [-s number_of_rows] [-p primary_keys] table_name csv_file
arguments:

options:
  -i        : only printing sql to make db table
  -d db_name: name of data base
              url is available: ex. sqlite:///db_file, mysql://user:password@localhost:3306/database_name
              if db_name was one without protocol, sqlite3 is assumed.
              if this option was omitted, assuming sqlite3 db file, what name is table_name+".sqlite" , will be created.
  -p primary_keys: primary keys, with csv format
  -s number_of_rows: number of scaned rows for creatign table


</pre>
## csv_to_db_shell.sh
<pre>
to insert csv data into database
Usage: csv_to_db_shell.sh [-d db_type] [-u db_user] [-p] [-c columns] db_name table_name index_name csv_file [sql]

arguments:
   db_name    : name of database. if db_type was "sqlite3", then that means name of file.
   table_name : name of table
   index_name : name of column that means index/primary key.
   csv_file   : name of csv file, that has names of columns at first row.
   sql        : sql statments that will be executed at first.

options:
   -d db_type : name of database, [mysql,sqlite3]: default=sqlite3
   -u db_user : user name for database
   -c columns : selected columns. ex. 1-5,20-30
   -p         : dump sql string, without execution

example: 
  csv_to_db_shell.sh -d mysql -u root sampleDB testTBL ID sample.csv "use sampleDB;DROP TABLE IF EXISTS testTBL;"
  csv_to_db_shell.sh -d sqlite3 sampleDB.sqlite3 testTBL ID sample.csv "DROP TABLE IF EXISTS testTBL;"

remark:
  charcode in csv_file must be utf-8.
  in db, type of data for each columns is VARCHAR(256) for mysql or TEXT for sqlite3. 
  if you want to change the type, use '-p' and edit sql statements that is executed by hand. 
  or you may use 'head -20 csv_file | csvsql -i db_type' to make sql statements for creating table.
  As assumption, there is only one header row in csv file.

  Alse you can use 'csvsql --overwrite --tables table_name --db db_type:///csv_file --insert csv_file'
  


</pre>
## csv_to_html.sh
<pre>
convert csv file into html format
Usage: csv_to_html.sh [-c columns] [-r row0,row1] csv_file
arguments:
  csv_file : path of csv file
options:
  -c columns: list of columns, ex. 1,5-10
  -r row0,row1 : range of rows to print


</pre>
## csv_wc.sh
<pre>
command like 'wc' for csv
Usage: csv_wc.sh (-c|-r|-t) csv_file
options:
  -c : number of columns
  -r : number of rows
  -t : line terminator
remark:
  as assumption, there is only one header row in csv file.
  number of rows means one without header row.
</pre>
