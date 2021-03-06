# -*- coding: utf-8 -*-

# import cPickle as pickle
import pickle
import argparse as ap

import numpy as np
import matplotlib.pyplot as plt

import antibarrel.common as common


def show(im, labels):
    fig, pl = plt.subplots(1, 2, sharex=True, sharey=True, squeeze=True)
    pl[0].imshow(im, cmap=plt.cm.gray)
    pl[0].set_xlabel("x [px]")
    pl[0].set_ylabel("y [px]")
    # We want to make the background and insignificant labels darkest.
    labels_good = labels.copy()
    labels_good[labels <= 0] = labels.max() + 1
    pl[1].imshow(labels_good, cmap=plt.cm.hot_r)
    pl[1].set_xlabel("x [px]")
    # vvv not needed, we have sharey of parallel images
    # pl[1].set_ylabel("y [px]")

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


def main():
    args = parse_args()
    with open(args.input, "rb") as infile:
        inp = pickle.load(infile)

    img = common.get_img(inp["srcim"])
    show(img, inp["labels"])


if __name__ == "__main__":
    main()
