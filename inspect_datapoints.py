# -*- coding: utf-8 -*-

# import cPickle as pickle
import pickle
import argparse as ap

import matplotlib.pyplot as plt

import common


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument("input")
    args = parser.parse_args()
    return args


def plot_points(ys, pts):
    _, pl = plt.subplots()
    for ptcoll in pts:
        pl.plot(ptcoll[:, 1], ptcoll[:, 0], "o", color="b")
    for ycoord in ys:
        pl.axhline(ycoord)
    plt.grid()


def do():
    args = parse_args()
    with open(args.input, "rb") as infile:
        inp = pickle.load(infile)

    common.show_points_more(inp["lines"], (inp["quad_fits"], inp["lin_fits"]))
    plot_points(inp["yvals"], inp["points"])
    plt.show()


if __name__ == "__main__":
    do()
