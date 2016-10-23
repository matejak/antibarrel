# -*- coding: utf-8 -*-

# import cPickle as pickle
import pickle
import argparse as ap

import numpy as np
import scipy.optimize as opt

import common


NORM = None


def pol2cart(rho, phi):
    rho *= NORM
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return np.array((y, x), float)


def _row2val(vals, rho, ysf):
    """
    Args:
        vals: The current solution
        rho: The radius of the current poin
        ysf: The constant coeff of the line (the point is on) over sine of the
            azimuth normed (:math:`y_0 / \\sin(\\varphi) / N`)

    Return:
        float - something that should ideally be zero, but can be any number.
    """
    ys = np.ones(4) * ysf
    for idx in range(3):
        ys[:(-idx - 1)] *= ysf
    # ^^^ should result in
    # ^^^ y^4, y^3, y^2, y
    ret = 0
    # vvv should be equal to rho
    ret += (vals * ys).sum()
    ret -= rho
    # TODO: Why not to return abs(ret)
    return ret


def _vals2val(vals, matrix, init_estim):
    """
    Args:
        vals: The current solution ---
            (a, b, c, d, <n-times the constant coeff>), first 4 are the solution
            we seek, rest is auxiliary.
        matrix: The second output of :func:`formulate`
        init_estim
    """
    fun = 0
    for row in matrix:
        # row = (\rho, \sin(\varphi), index
        # inc = _row2val(<solution>, <\rho>, <the current estimate of y_0> /
        # <sin(\varphi)> / NORM
        inc = _row2val(vals[:4], row[0], vals[4 + int(row[2])] / row[1] / NORM)
        # fun += abs(inc)
        fun += inc ** 2
    # print(vals, abs(fun))
    bad = 0
    # bad += np.abs((init_estim - vals)[4:]).sum() * 0.1
    fun += bad
    return fun


def formulate(all_points, yvals):
    """
    Args:
        all_points (list of lists): List of points on curved lines.
        yvals (array): Numbers close to constant coefficients of lines.

    Returns:
        tuple - (initial estimation
        all points --- array where each point has
        :math:`(\\rho, \\sin(\\varphi), i)`, where :math:`i` is the line index)

    .. note::
        Point is a coordinate pair (y, x)
    """
    # a, b, c, d + n-times y0
    n_unks = 4 + len(all_points)
    result = np.zeros(n_unks, float)
    result[3] = 1
    # defaults are a, b, c, d
    #           == 0, 0, 0, 1
    data = np.zeros((len(all_points[0]) * len(all_points), 3))
    # values are R, sf, idx

    ptidx = 0
    for polyidx, points in enumerate(all_points):
        result[4 + polyidx] = yvals[polyidx]
        for pt in points:
            rho, phi = common.cart2pol(pt[0], pt[1])
            sphi = np.sin(phi)
            data[ptidx, 0] = rho
            data[ptidx, 1] = sphi
            data[ptidx, 2] = polyidx
            ptidx += 1
    return result, data


def solve(estimate, data):
    """
    Supply output of :func:`formulate`

    Returns:
        tuple - First go the aberration coeffs,
            then the computed constant coeffs
    """
    # print("Initial: ", _vals2val(estimate, data, estimate), file=sys.stderr)
    meth = "Powell"
    res = opt.minimize(_vals2val, estimate, args=(data, estimate),
                       method=meth).x
    # print("Final: ", res[:4], _vals2val(res, data, estimate), file=sys.stderr)
    # print("Line shift: ",
    #       res[4:] - estimate[4:], _vals2val(res, data, estimate),
    #       file=sys.stderr)
    return res


def get_result(all_points, yvals, imgsize):
    global NORM
    halves = np.array(imgsize, int) // 2
    NORM = halves.min()
    estim, data = formulate(all_points, yvals)
    result = solve(estim, data)
    return result


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()
    return args


def do():
    args = parse_args()
    indata = []
    with open(args.input, "rb") as infile:
        indata = pickle.load(infile)

    output = get_result(indata["points"], indata["yvals"], indata["imgsize"])
    outstr = ("{},{},{},{}"
              .format(* output))

    with open(args.output, "w") as outfile:
        outfile.write(outstr)


if __name__ == "__main__":
    do()
