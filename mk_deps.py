# -*- coding: utf-8 -*-

# import cPickle as pickle
import pickle
import argparse as ap

import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt

import statsmodels.formula.api as sfapi
# import skimage as si
# import skimage.measure


def residue_x(coeffs, x, y):
    lin, x0 = coeffs
    ret = y - (x0 + lin * x)
    return ret


def preclean_rough(xs, ys):
    hi = np.percentile(ys, 80)
    lo = np.percentile(ys, 20)
    span = hi - lo
    bound_lo = lo - span
    bound_hi = hi + span
    is_ok = (bound_lo < ys) * (ys < bound_hi)
    return xs[is_ok], ys[is_ok]


def robust_fit(xs, ys):
    xs, ys = preclean_data(xs, ys)
    res_robust = opt.least_squares(residue_x, np.zeros(2), method="dogbox",
                                   loss='arctan', args=(xs, ys), verbose=0)
    return res_robust["x"]


def preclean_data(xs, ys):
    norig = len(xs)
    xs, ys = preclean_rough(xs, ys)
    for _ in range(3):
        regression = sfapi.ols("data ~ x", data=dict(data=ys, x=xs)).fit()

        test = regression.outlier_test()
        # The greater t is, the more outliers there will be
        # print(test.iloc[:, 2])
        selection = [i for i, t in enumerate(test.iloc[:, 1]) if t > 0.15]
        selection = np.array(selection, int)

        xs = xs[selection]
        ys = ys[selection]

    noutliers = norig - len(xs)
    print("Removed total {} outliers".format(noutliers))

    """
    import statsmodels.api
    import statsmodels.graphics as smgraphics

    figure = smgraphics.regressionplots.plot_fit(regression, 1)
    smgraphics.regressionplots.abline_plot(
        model_results=regression, ax=figure.axes[0])
    """

    return xs, ys


def get_result(lines):
    quads, lins, dsts = [np.array(x) for x in zip(* lines)]
    fit = robust_fit(dsts, quads)
    fit_quad = fit

    fit = robust_fit(dsts, lins)
    fit_lin = fit

    lines_out = (quads, lins, dsts)

    zero_at = np.roots(fit_quad)[0]
    slope = np.polyval(fit_lin, zero_at)

    output = dict(
        fits=np.array(lines),
        lines_out=lines_out,
        fit_quad=fit_quad,
        fit_lin=fit_lin,
        zero_at=zero_at,
        slope=slope,
    )
    return output


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument("input",
                        help="Pass the filename of the output of 'label.py'")
    parser.add_argument("output")
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    return args


def do():
    args = parse_args()
    with open(args.input, "rb") as infile:
        indata = pickle.load(infile)
    lines = indata["lines"]
    output = get_result(lines)
    indata.update(output)
    with open(args.output, "wb") as outfile:
        pickle.dump(output, outfile)


if __name__ == "__main__":
    do()
