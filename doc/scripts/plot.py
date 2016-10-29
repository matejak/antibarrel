
import argparse as ap

import numpy as np
import pylab as pyl


def main():
    args = parse_args()
    pts = [float(x) for x in args.pts.split(",") if len(x) > 0]
    tform = [float(x) for x in args.tform.split(",")]

    def _tform(dom):
        poly = np.array(tform + [0])
        ret = np.polyval(poly, dom)
        return ret

    fig, plt = pyl.subplots(figsize=[float(x) for x in args.size.split(",")])
    # plot_dep(plt, _tform)
    plot_points_dep(plt, _tform, pts)
    fig.savefig(args.output)


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument("--tform", default="0,0,0,1")
    parser.add_argument("--pts", default="")
    parser.add_argument("output")
    parser.add_argument("--size", default="6,6")
    parser.add_argument("--dpi", default=150, type=float)
    args = parser.parse_args()
    return args


def plot_dep(plt, func):
    _plot_dep(plt, func)
    plt.grid()
    plt.legend(loc="best")


def _plot_dep(plt, func):
    _max = 1.8
    dom = np.linspace(0, _max, 200)
    linear = dom.copy()
    ours = func(dom)
    plt.plot(dom, linear, "--", label="no distortion")
    plt.plot(dom, ours, "-", label="distortion")
    plt.set_xlim(0, _max)
    plt.set_ylim(0, _max)
    return dom


def plot_points_dep(plt, func, pts):
    plt.grid()
    _plot_dep(plt, func)
    for pt in pts:
        plt.plot(pt, pt, "or", alpha=0.5)
        plt.plot(pt, func(pt), "or")


def plot_points_img(plt, func, pts):
    for pt in pts:
        plt.plot(pt, pt, "or")
        plt.plot(pt, func(pt), "or")
    plt.grid()
    plt.legend(loc="best")


if __name__ == "__main__":
    main()
