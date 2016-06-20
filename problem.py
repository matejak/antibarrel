# -*- coding: utf-8 -*-

import sys
import pickle
import argparse as ap

import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt


NORM = None


def cart2pol(pt):
    x = pt[1]
    y = pt[0]
    rho = np.sqrt(x ** 2 + y ** 2) / NORM
    phi = np.arctan2(y, x)
    return(rho, phi)


def pol2cart(rho, phi):
    rho *= NORM
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return np.array((y, x), float)


def _row2val2(vals, rho, ysf):
    ys = np.ones(4) * rho
    for idx in range(3):
        ys[:(-idx - 1)] *= rho
    # ^^^ should result in
    # ^^^ y^4, y^3, y^2, y
    ret = 0
    ret -= ysf
    ret += (vals * ys).sum()
    return ret


def _row2val(vals, rho, ysf):
    ys = np.ones(4) * ysf
    for idx in range(3):
        ys[:(-idx - 1)] *= ysf
    # ^^^ should result in
    # ^^^ y^4, y^3, y^2, y
    ret = 0
    ret -= rho
    ret += (vals * ys).sum()
    return ret


# vals: a, b, c, d, + n-times y0
# matrix row: R, sf, idx
def _vals2val(vals, matrix, init_estim):
    fun = 0
    for row in matrix:
        inc = _row2val(vals[:4], row[0], vals[4 + int(row[2])] / row[1] / NORM)
        # fun += abs(inc)
        fun += inc ** 2
    # print(vals, abs(fun))
    bad = 0
    # bad += np.abs((init_estim - vals)[4:]).sum() * 0.1
    fun += bad
    return fun


def formulate(fit_quad, center, limits):
    """
    Returns:
        tuple - result, data, all_points

    .. note::
        Point is a coordinate pair (y, x)
    """
    ylim, xlim = limits
    xlim = ylim
    polys = [(np.polyval(fit_quad, const), 0, const)
             for const in np.linspace(1e-1,  1, 13) ** 2 * ylim]
    # a, b, c, d + n-times y0
    n_unks = 4 + len(polys)
    PTS_IN_POLY = 15
    result = np.zeros(n_unks, float)
    result[3] = 1
    # defaults are a, b, c, d
    #           == 0, 0, 0, 1
    data = np.zeros((PTS_IN_POLY * len(polys), 3))
    # values are R, sf, idx

    all_points = []
    ptidx = 0
    for polyidx, poly in enumerate(polys):
        result[4 + polyidx] = poly[-1]
        points = [(np.polyval(poly, dom), dom)
                  for dom in np.linspace(1e-1, 1, PTS_IN_POLY) ** 2 * xlim]
        for pt in points:
            rho, phi = cart2pol(pt)
            sphi = np.sin(phi)
            data[ptidx, 0] = rho
            data[ptidx, 1] = sphi
            data[ptidx, 2] = polyidx
            ptidx += 1
        all_points.extend(points)
    all_points = np.array(all_points)

    return result, data, all_points


def solve(estimate, data):
    print("Initial: ", _vals2val(estimate, data, estimate), file=sys.stderr)
    meth = "Powell"
    res = opt.minimize(_vals2val, estimate, args=(data, estimate),
                       method=meth).x
    print("Final: ", res[:4], _vals2val(res, data, estimate), file=sys.stderr)
    print("Line shift: ",
          res[4:] - estimate[4:], _vals2val(res, data, estimate),
          file=sys.stderr)
    return res


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    return args


def plot_pts(ys, * pts):
    _, pl = plt.subplots()
    for ptcoll in pts:
        pl.plot(ptcoll[:, 1], ptcoll[:, 0], "o")
    for ycoord in ys:
        pl.axhline(ycoord)
    plt.grid()
    plt.show()


def print_diffs(ys, bad, good):
    pnum = len(bad)
    pts_in_row = pnum // len(ys)
    diffs = np.zeros(pnum * 2)
    bad_sum = 0
    for idx, pt in enumerate(bad):
        diffs[idx] = pt[0] - ys[idx / pts_in_row]
        bad_sum += (diffs[idx]) ** 2
    print("Bad sum: ", bad_sum, file=sys.stderr)
    good_sum = 0
    for idx, pt in enumerate(good):
        diffs[idx + pnum] = pt[0] - ys[idx / pts_in_row]
        good_sum += (diffs[idx + pnum]) ** 2
    print("Good sum: ", good_sum, file=sys.stderr)
    _, pl = plt.subplots()
    pl.hist(np.abs(diffs[:pnum]), bins=15)
    pl.hist(-np.abs(diffs[pnum:]), bins=15)
    pl.grid()
    plt.show()


def tform_pts(tform, pts):
    res = []
    for pt in pts:
        rho, phi = cart2pol(pt)
        # find polyroot of [* tform, rhovec]
        if 1:
            poly = np.array((tform[0], tform[1], tform[2], tform[3], - rho))
            roots = np.roots(poly)
            diff = np.abs(rho - roots)
            rho2 = roots[np.argmin(diff)].real
        else:
            rho2 = (tform * rho ** np.arange(4, 0, -1)).sum()
        pt2 = pol2cart(rho2, phi)
        res.append(pt2)
    res = np.array(res)
    return res


def main():
    args = parse_args()
    with open(args.input, "rb") as infile:
        indata = pickle.load(infile)

    center = indata["center"]
    global NORM
    halves = np.array(indata["imgsize"], int) // 2
    NORM = halves.min()
    quads = indata["key_deps"].mean(axis=0)
    estim, data, points = formulate(quads, center, halves)
    result = solve(estim, data)
    print("{} {} {} {} {},{}".format(
        result[0], result[1], result[2], result[3], center[1], center[0])
    )
    if args.plot:
        shifted = tform_pts(result[:4], points)
        plot_pts(result[4:], points, shifted)
        print_diffs(result[4:], points, shifted)


if __name__ == "__main__":
    main()
