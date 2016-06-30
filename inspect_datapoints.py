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


def do():
    args = parse_args()
    with open(args.input, "rb") as infile:
        inp = pickle.load(infile)

    """
    center=center,
    imgsize=imgsize,
    quad_fits=quad_fits,
    lin_fits=lin_fits,
    lines=lines,
    points=points,
    """

    common.show_points_more(inp["lines"], (inp["quad_fits"], inp["lin_fits"]))
    plt.show()


if __name__ == "__main__":
    do()
