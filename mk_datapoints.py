# -*- coding: utf-8 -*-

# import cPickle as pickle
import pickle
import argparse as ap

import numpy as np
import scipy.optimize as opt

import common


def get_points(fit_quad, limits):
    """
    Returns:
        tuple - result, data, all_points

    .. note::
        Point is a coordinate pair (y, x)
    """
    ylim, xlim = limits
    xlim = ylim
    consts = np.linspace(1e-1,  1, 13) ** 2 * ylim
    polys = [(np.polyval(fit_quad, const), 0, const)
             for const in consts]
    # a, b, c, d + n-times y0
    PTS_IN_POLY = 15
    # defaults are a, b, c, d
    #           == 0, 0, 0, 1
    # values are R, sf, idx

    all_points = []
    for polyidx, poly in enumerate(polys):
        points = [(np.polyval(poly, dom), dom)
                  for dom in np.linspace(1e-1, 1, PTS_IN_POLY) ** 2 * xlim]
        all_points.append(np.array(points, float))

    return all_points, consts


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument("input", nargs="+",
                        help="The deps pickles.")
    parser.add_argument("--center")
    parser.add_argument("output")
    args = parser.parse_args()
    return args


def do():
    args = parse_args()
    indata = []
    for fname in args.input:
        with open(fname, "rb") as infile:
            indata.append(pickle.load(infile))

    quad_fits = [dat["fit_quad"] for dat in indata]
    quad_mean = np.array(quad_fits, float).mean(axis=0)
    lin_fits = [dat["fit_lin"] for dat in indata]
    lines = [np.array(dat["lines"]) for dat in indata]

    img = common.get_img(indata[-1]["srcim"])
    imgsize = np.array(img.shape, int)

    center = args.center

    points, yvals = get_points(quad_mean, imgsize // 2)

    output = dict(
        center=center,
        imgsize=imgsize,
        quad_fits=quad_fits,
        lin_fits=lin_fits,
        lines=lines,
        points=points,
        yvals=yvals,
    )

    with open(args.output, "wb") as outfile:
        pickle.dump(output, outfile)


if __name__ == "__main__":
    do()
