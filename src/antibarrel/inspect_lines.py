# -*- coding: utf-8 -*-

# import cPickle as pickle
import pickle
import argparse as ap

import numpy as np
import matplotlib.pyplot as plt

import antibarrel.common


def show_lines(img, lines, center=(0, 0)):
    fig, pl = plt.subplots(1, 1)
    extent = np.array((0, img.shape[1], 0, img.shape[0]))
    extent[:2] -= center[1]
    extent[2:] -= center[0]
    pl.imshow(img, cmap=plt.cm.gray, extent=extent, origin="lower")
    dom = np.arange(img.shape[1]) - center[1]
    pl.autoscale(False)
    for line in lines:
        hom = np.polyval(line, dom)
        mult = 1e7
        label = "a⋅{:.3g} = {:.3g}".format(mult, line[-3] * mult)
        pl.plot(dom, hom, label=label)
    leg = pl.legend(fancybox=True)
    leg.get_frame().set_alpha(0.7)


def show_points(lines):
    _, pl_quad = plt.subplots()
    _, pl_lin = plt.subplots()

    def idx2alpha(idx): return 1 - 0.8 * (idx / len(lines))

    for idx, line in enumerate(lines):
        alpha = idx2alpha(idx)
        pl_quad.plot(line[-1], line[-3], "ob", alpha=alpha)
        # pl.plot(dsts, lins, "o")

        pl_lin.plot(line[-1], line[-2], "og", alpha=alpha)
        # pl.plot(dsts, lins, "o")

    pl_quad.grid()
    pl_quad.axhline(0, color="k")
    pl_quad.set_title("Quadratic term")

    pl_lin.grid()
    pl_lin.set_title("Linear term")


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--show", default="3-8", help="Range of indices")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    with open(args.input, "rb") as infile:
        inp = pickle.load(infile)

    img = common.get_img(inp["srcim"])
    lines = inp["lines"]

    toshow = [int(idx) for idx in args.show.split("-")]
    toshow = slice(toshow[0], toshow[1])
    show_lines(img, lines[toshow], inp.get("center", (0, 0)))
    common.show_points(lines)
    plt.show()


if __name__ == "__main__":
    main()
