# -*- coding: utf-8 -*-

# import cPickle as pickle
import pickle
import argparse as ap

import matplotlib.pyplot as plt

import antibarrel.common as common


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument("input")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    with open(args.input, "rb") as infile:
        inp = pickle.load(infile)

    lines = inp["lines"]
    deps = [inp[key] for key in ("fit_quad", "fit_lin")]

    common.show_points(lines, deps)
    plt.show()


if __name__ == "__main__":
    main()
