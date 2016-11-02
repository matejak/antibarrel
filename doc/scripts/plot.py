# -*- coding: utf-8 -*-
import argparse as ap

import numpy as np
import pylab as pyl

import common


def main():
    args = parse_args()
    pts = [float(x) for x in args.pts.split(",") if len(x) > 0]
    tform = [float(x) for x in args.tform.split(",")]

    def _tform(dom):
        poly = np.array(tform + [0])
        ret = np.polyval(poly, dom)
        return ret

    figsize = [float(x) for x in args.size.split(",")]
    fig, plt = pyl.subplots(figsize=figsize, dpi=args.dpi)
    plot_dep(plt, _tform)
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
    common._plot_dep(plt, func)
    plt.grid()
    plt.legend(loc="best")


if __name__ == "__main__":
    main()
