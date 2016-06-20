# -*- coding: utf-8 -*-

# import cPickle as pickle
import pickle
import argparse as ap

import numpy as np
import scipy.ndimage as ndim
import scipy.optimize as opt
import matplotlib.pyplot as plt

import statsmodels.formula.api as sfapi
# import skimage as si
# import skimage.measure

import common


def make_fit(orig, masked, idx, grow=6, center=None):
    """
    Given original array, the labelled one, label and positionss of the
    zero coordinate, return a polynomial fit for hte respective line.
    """
    mask = (masked == idx)  # .astype(int)
    grown = mask.copy()
    grown = ndim.morphology.binary_dilation(grown, iterations=grow)
    if 0:
        _, pl = plt.subplots()
        base = mask.copy().astype(float)
        base += grown.copy().astype(float)
        base += orig / orig.max()
        pl.imshow(base)
        plt.show()

    y, x = np.where(grown)
    if center is not None:
        x -= center[1]
        y -= center[0]
    fit = np.polyfit(x, y, 2, w=orig[grown] ** 2)
    return fit


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument("input",
                        help="Pass the filename of the output of 'label.py'")
    parser.add_argument("output")
    parser.add_argument("--grow", type=int, default=6,
                        help="Pixel count threshold for rogh lines.")
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    return args


def do():
    args = parse_args()
    with open(args.input, "rb") as infile:
        indata = pickle.load(infile)
    try:
        img = common.get_img(indata["srcim"])
    except Exception:
        raise
    ordered_labels = indata["labels"]
    center = indata.get("center", None)
    lines = [make_fit(img, ordered_labels, label, args.grow, center)
             for label in range(1, int(ordered_labels.max()))]
    indata["lines"] = lines

    with open(args.output, "wb") as outfile:
        pickle.dump(indata, outfile)


if __name__ == "__main__":
    do()
