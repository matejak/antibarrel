# -*- coding: utf-8 -*-
import argparse as ap

import numpy as np
import pylab as pyl

import common


def main():
    args = parse_args()
    pts = [float(x) for x in args.pts.split(",") if len(x) > 0]
    pts = np.linspace(0, pts[0], int(pts[1]))
    tform = [float(x) for x in args.tform.split(",")]

    def _tform(dom):
        poly = np.array(tform + [0])
        ret = np.polyval(poly, dom)
        return ret

    figsize = [float(x) for x in args.size.split(",")]
    fig, plt = pyl.subplots(figsize=figsize, dpi=args.dpi)
    # plot_dep(plt, _tform)
    plot_pts(plt, _tform, pts)
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


def plot_pts(plt, func, pts):
    for pt in pts:
        plt.plot(pt, 1, "ob")
        plt.plot(func(pt), 1.1, "or")
        plt.plot([pt, func(pt)], [1, 1.1], "-k", alpha=0.5)
    plt.set_yticks([1, 1.1])
    plt.set_yticklabels(["real", "distorted"])
    plt.grid()
    plt.set_xlabel("radius / a.u.")


if __name__ == "__main__":
    main()
