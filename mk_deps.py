# -*- coding: utf-8 -*-


import pickle
import argparse as ap

import numpy as np
import scipy.optimize as opt

import statsmodels.formula.api as sfapi


def residue_x(coeffs, x, y):
    lin, x0 = coeffs
    ret = y - (x0 + lin * x)
    return ret


def preclean_rough(xs, ys):
    """
    Takes out values that are either too high or too high.
    It works with 80 and 20 percentile of ``ys`` :math:`y_20` and :math:`y_80`.
    The difference :math:`y_80 - y_20` is ``span``
    and every ``y`` from ``ys`` (and the corresponding ``x``)
    lower than :math:`y_20 - span` or greater than :math:`y_80 + span`
    is purged.
    """
    hi = np.percentile(ys, 80)
    lo = np.percentile(ys, 20)
    span = hi - lo
    bound_lo = lo - span
    bound_hi = hi + span
    is_ok = (bound_lo < ys) * (ys < bound_hi)
    return xs[is_ok], ys[is_ok]


def robust_fit(xs, ys):
    """
    Given x and y values, first remove probable outliers and then
    perform robust fit.
    """
    xs, ys = preclean_data(xs, ys)
    res_robust = opt.least_squares(residue_x, np.zeros(2), method="dogbox",
                                   loss='arctan', args=(xs, ys), verbose=0)
    return res_robust["x"]


def preclean_data(xs, ys):
    """
    First of all, remove apparent outliers, then remove outliers that are not
    so apparent.
    """
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

    if 0:
        noutliers = norig - len(xs)
        print("Removed total {} outliers".format(noutliers))

        # vvv may be needed, even if it doesn't seem so
        import statsmodels.api
        import statsmodels.graphics as smgraphics

        figure = smgraphics.regressionplots.plot_fit(regression, 1)
        smgraphics.regressionplots.abline_plot(
            model_results=regression, ax=figure.axes[0])

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
        lines_out=lines_out,
        fit_quad=fit_quad,
        fit_lin=fit_lin,
        zero_at=zero_at,
        slope=slope,
    )
    return output


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument(
        "input", help="Pass the filename of the output of 'mk_lines.py'")
    parser.add_argument("output")
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
        pickle.dump(indata, outfile)


if __name__ == "__main__":
    do()
