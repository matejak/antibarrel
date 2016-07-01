# -*- coding: utf-8 -*-

# import cPickle as pickle
import pickle
import argparse as ap

import numpy as np
import matplotlib.pyplot as plt

import common


def show(im, labels):
    fig, pl = plt.subplots(1, 2, sharex=True, sharey=True, squeeze=True)
    pl[0].imshow(im, cmap=plt.cm.gray)
    # We want to make the background and insignificant labels darkest.
    labels_good = labels.copy()
    labels_good[labels <= 0] = labels.max() + 1
    pl[1].imshow(labels_good, cmap=plt.cm.hot_r)

    labels_bad = labels.copy()
    labels_bad[labels < 0] = 10
    labels_bad[labels >= 0] = float("NaN")  # transparent
    pl[1].imshow(labels_bad, vmin=0, vmax=100, cmap=plt.cm.winter)
    # fig.colorbar(plo)
    plt.show()


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument("input")
    args = parser.parse_args()
    return args


def do():
    args = parse_args()
    with open(args.input, "rb") as infile:
        inp = pickle.load(infile)

    img = common.get_img(inp["srcim"])
    show(img, inp["labels"])


if __name__ == "__main__":
    do()
