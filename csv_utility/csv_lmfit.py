#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Name:         csv_lmfit.py
# Description:
#
# Author:       m.akei
# Copyright:    (c) 2020 by m.na.akei
# Time-stamp:   <2020-10-11 15:58:11>
# Licence:
#  Copyright (c) 2021 Masaharu N. Akei
#
#  This software is released under the MIT License.
#    http://opensource.org/licenses/mit-license.php
# ----------------------------------------------------------------------
import argparse
import textwrap
import sys

from pathlib import Path
import importlib
import re
import json

# Non-Linear Least-Squares Minimization and Curve-Fitting for Python  Non-Linear Least-Squares Minimization and Curve-Fitting for Python https://lmfit.github.io/lmfit-py/index.html
import lmfit as lmf
import lmfit.models as lmfm

import pandas as pd

VERSION = 1.0

MODEL_SAMPLE = '''
def model_init():
    # Parameter and Parameters  Non-Linear Least-Squares Minimization and Curve-Fitting for Python https://lmfit.github.io/lmfit-py/parameters.html
    result = {
        "a": {
            "value": 0,
            "min": -1,
            "max": 5,
            "vary": True
        },
        "b": {
            "value": 1,
            "min": -3,
            "max": 3,
            "vary": True
        },
        "c": {
            "value": 1,
            "min": -1,
            "max": 1,
            "vary": True
        }
    }
    return result
def model_function(x, a, b, c):
    result = a * x**2 + b * x + c
    return result
'''

#---- internal model
import scipy.stats as sps


class BetaDistributionModel():
    '''Beta Distribution
    '''
    @staticmethod
    def model_hint():
        message = """
xmax-xmin <= 1.0
"""
        return message

    @staticmethod
    def model_init():
        result = {
            "alpha": {
                "value": 1,
                "min": 0.0001,
                "vary": True
            },
            "beta": {
                "value": 1,
                "min": 0.0001,
                "vary": True
            },
            "loc": {
                "value": 0,
                "vary": True
            },
            "scale": {
                "value": 1,
                "min": 0.0001,
                "vary": True
            }
        }
        return result

    @staticmethod
    def model_function(x, alpha, beta, loc, scale):
        return sps.beta.pdf(x, alpha, beta, loc, scale)


class BinomialDistributionModel():
    '''Binomial Distribution
    '''
    @staticmethod
    def model_hint():
        message = """
you msut give paramter 'n' definition with '--model_definition'.
'n' must be more than xmax-xmin.
"""
        return message

    @staticmethod
    def model_init():
        result = {
            "n": {
                "value": 100,
                "vary": False
            },
            "p": {
                "value": 0.5,
                "min": 0.0,
                "max": 1.0,
                "vary": True
            },
            "loc": {
                "value": 0,
                "vary": True
            },
        }
        return result

    @staticmethod
    def model_function(x, n, p, loc):
        return sps.binom.pmf(x, n, p, loc=loc)


INTERNAL_MODELS = [BetaDistributionModel, BinomialDistributionModel]


def init():
    arg_parser = argparse.ArgumentParser(description="fitting function to data in csv file",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''
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
'''))

    arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    arg_parser.add_argument("--model_definition",
                            dest="MODEL",
                            help="model definition, 'model_name|json string or @json file', see example",
                            type=str,
                            action='append',
                            metavar='MODEL_NAME|JSON')

    arg_parser.add_argument("--xrange", dest="XRANGE", help="range of X", type=str, metavar="X_MIN,X_MAX", default=None)

    arg_parser.add_argument("--output_file", dest="OUTPUT", help="path of output file", default=None)
    arg_parser.add_argument("--remove_offset", dest="DCOFFSET", help="remove dc offset", action="store_true", default=False)
    arg_parser.add_argument("--print_parameters", dest="PPARAMS", help="only print paramters", action="store_true", default=False)

    arg_parser.add_argument("--print_sample_model",
                            dest="PRINT_M",
                            help="print sample code for model into stdout",
                            action="store_true",
                            default=False)
    arg_parser.add_argument("--list_internal", dest="LIST_I", help="show list of internal models", action="store_true", default=False)

    arg_parser.add_argument('csv_file', metavar='CSV_FILE', help='files to read, if empty, stdin is used', default=None, nargs="?")
    arg_parser.add_argument('x_column', metavar='COLUMN', help='name of x column', default=None, nargs="?")
    arg_parser.add_argument('y_column', metavar='COLUMN', help='name of y column', default=None, nargs="?")
    args = arg_parser.parse_args()
    return args, arg_parser


def get_output_file(outname_func, input_file, output_file, buffered=False):
    """retriev path of output file from path of 'input file'.
       if 'output_file' was defined, then the value will be returned.
       if 'output_file' was not defined, then 'output_file' will be derived from 'input_file'.

    :param outname_func: function to make output file name, function has path of input file as only one argument.
    :param input_file: path of input file
    :param output_file: path of output file
    :param buffered: if True and input_file=="-", then sys.stdout.buffer as output_file will be returned.
                     if False, sys.stdout will be returned.
    :returns: path of output file or sys.stdout[.buffer]
    :rtype: str or file handler

    :exmple:
          output_file = get_output_file(lambda x: Path(x).stem + "_test.csv", input_file, output_file)


    """
    # output_file = Path(input_file).stem + "_hist.csv"
    if output_file is None or len(output_file) == 0:
        if isinstance(input_file, str) and input_file != "-":
            output_file = outname_func(input_file)
        else:
            if buffered:
                output_file = sys.stdout.buffer
            else:
                output_file = sys.stdout
    elif isinstance(output_file, str) and output_file == "-":
        if buffered:
            output_file = sys.stdout.buffer
        else:
            output_file = sys.stdout

    if input_file == "-":
        input_file = sys.stdin

    return output_file


def trim_output_file(output_file, mkdir=True, overwrite=True):
    """check path of output file

    :param output_file: path of output file
    :param mkdir: if True, do mkdir
    :param overwrite: if False and file existed, then exception will be raised.
    :returns: 
    :rtype: 

    """
    if isinstance(output_file, str):
        p_dir = Path(output_file).parent
        if mkdir and not Path(p_dir).exists():
            Path(p_dir).mkdir(exist_ok=True, parents=True)

        if not overwrite and Path(output_file).exists():
            raise Exception("{} already exists".format(output_file))


def parse_model_definition(model_s):
    cvs = re.split(r"\s*\|\s*", model_s)
    if len(cvs) == 0:
        print("??Error:csv_lmfit:invalid model deinition", file=sys.stderr)

    result = {}
    result["params"] = {}
    try:
        result["name"] = cvs[0]
        if not result["name"].startswith("@") and not result["name"].startswith("%"):
            result["model"] = importlib.import_module(cvs[0])
            if "model_init" in dir(result["model"]):
                result["params"].update(result["model"].model_init())
        if result["name"].startswith("%"):
            try:
                result["model"] = eval(result["name"][1:] + "()")
            except NameError as e:
                print("??Error:csv_lmfit:invalid internal model name: {}".format(result["name"][1:]), file=sys.stderr)
                print("         internal model wiht '%' prefix must be one of: {}".format([v.__name__ for v in INTERNAL_MODELS]),
                      file=sys.stderr)
                sys.exit(1)
            if "model_init" in dir(result["model"]):
                result["params"].update(result["model"].model_init())
    except ModuleNotFoundError as e:
        print("??Error:csv_lmfit:{} was not found: {}".format(cvs[0], e), file=sys.stderr)
        sys.exit(1)
    if len(cvs) > 1:
        if cvs[1].startswith("@"):
            with open(cvs[1][1:]) as fp:
                result["params"].update(json.load(fp))
        else:
            result["params"].update(json.loads(cvs[1]))

    return result


def print_internal_models():
    l_models = [v for v in dir(lmfm) if v.endswith("Model") and v not in ["Model", "ExpressionModel", "PolynomialModel"]]
    # for v in l_models:
    #     print(v)
    #     eval("lmfm." + v + "()")
    indent_mode = 2
    lmfm_models = [(v, eval("lmfm." + v + "()").make_params().dumps(indent=indent_mode)) for v in l_models]
    print("-- internal models with '@' prefix")
    for v1, v2 in lmfm_models:
        print("model name:{}\nparameters:\n{}\n".format(v1, v2))
    lmfm_models = [(v.__name__, json.dumps(v.model_init(), indent=indent_mode), v.model_hint()) for v in INTERNAL_MODELS]
    print("-- internal models with '%' prefix")
    for v1, v2, v3 in lmfm_models:
        print("model name:{}\nhint:{}\nparameters:\n{}\n".format(v1, v3, v2))


if __name__ == "__main__":
    args, arg_parser = init()
    csv_file = args.csv_file
    output_file = args.OUTPUT
    mds = args.MODEL

    x_column = args.x_column
    y_column = args.y_column
    x_range_s = args.XRANGE

    dc_offset = args.DCOFFSET
    print_params = args.PPARAMS
    list_internal = args.LIST_I
    print_sample_model = args.PRINT_M

    if list_internal:
        print_internal_models()
        sys.exit(0)
    if print_sample_model:
        print(MODEL_SAMPLE)
        sys.exit(0)

    if csv_file is None or x_column is None or y_column is None:
        arg_parser.print_help(file=sys.stderr)
        sys.exit(0)

    csv_df = pd.read_csv(csv_file)
    if x_range_s is None:
        x_values = csv_df[x_column]
        y_values = csv_df[y_column]
    else:
        x_range = [float(v) for v in re.split(r"\s*,\s*", x_range_s)]
        csv_df_2 = csv_df[(csv_df[x_column] > x_range[0]) & (csv_df[x_column] < x_range[1])]
        x_values = csv_df_2[x_column]
        y_values = csv_df_2[y_column]

    lmf_model = lmfm.ConstantModel(prefix="m0_")
    idx = 1
    init_params = {}
    model_list = {}
    for model_def_s in mds:
        res = parse_model_definition(model_def_s)
        pfx = "m{}_".format(idx)
        idx += 1
        if res["name"].startswith("@"):
            try:
                lmf_model += eval("lmfm." + res["name"][1:] + "(prefix='{}')".format(pfx))
            except AttributeError as e:
                print("??Error:csv_lmfit:invalid implicit model:{}:{}".format(res["name"][1:], e), file=sys.stderr)
                print("see Built-in Fitting Models in the models module https://lmfit.github.io/lmfit-py/builtin_models.html",
                      file=sys.stderr)
                sys.exit(1)
        else:
            lmf_model += lmf.Model(res["model"].model_function, prefix=pfx)
        model_list[res["name"]] = {"prefix": pfx}
        if "params" in res:
            for p_key, p_def in res["params"].items():
                model_list[res["name"]].update({p_key: pfx + p_key})
                init_params[pfx + p_key] = p_def

    params = lmf_model.make_params()
    params["m0_c"].set(value=0, vary=dc_offset)

    for p_key, p_def in init_params.items():
        if p_key in params:
            params[p_key].set(**p_def)
        else:
            print("??Error:csv_lmfit:invalid parameter name:{}".format(p_key), file=sys.stderr)

    print("-- prefix for each model")
    print("dc_offset:prefix=m0_")
    for mdl, ks in model_list.items():
        for k in ks:
            if k == "prefix":
                print("{}:{}={}".format(mdl, k, ks[k]))
    print("-- initial parameter")
    print(params.pretty_print())
    print("removing_dc_offset mode: {}".format(dc_offset))

    if print_params:
        sys.exit(0)

    # methods: https://lmfit.github.io/lmfit-py/fitting.html#choosing-different-fitting-methods
    fit_result = lmf_model.fit(y_values, params, x=x_values, method="leastsq")
    # fig, gridspec = fit_result.plot(data_kws={'markersize': 5})

    if not fit_result.success:
        print("??Error:csv_lmfit:fitting was failed:{},{}".format(fit_result.message, fit_result.lmdif_message), file=sys.stderr)
        sys.exit(1)

    print("-- result of fitting")
    # if dc_offset:
    #     print("dc offset:{}".format(fit_result.best_values["m0_c"]))
    # for mdl, ks in model_list.items():
    #     for k in ks:
    #         if k != "prefix":
    #             print("{}:{}={}".format(mdl, k, fit_result.best_values[ks[k]]))
    print(fit_result.params.pretty_print())

    print("-- report of fitting")
    print(fit_result.fit_report())
    if fit_result.errorbars:
        print("-- confidence intervals of fitting")
        print(fit_result.ci_report())

    if output_file is not None:
        out_df = pd.DataFrame(columns=["X", "Y0", "Y_fitted", "DY"])
        out_df["X"] = x_values
        out_df["Y0"] = y_values
        out_df["Y_fitted"] = fit_result.best_fit
        out_df["DY"] = fit_result.residual
        out_df.to_csv(output_file, index=False)
        print("-- {} was cretaed".format(output_file), file=sys.stderr)
