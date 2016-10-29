# -*- coding: utf-8 -*-

import pickle
import argparse as ap
import logging
import sys

import numpy as np
import scipy.ndimage as ndim

import common


def make_fit(orig, masked, idx, grow=6, center=None):
    """
    Given original array, the labelled one, label and positionss of the
    zero coordinate, return a polynomial fit for hte respective line.
    """
    mask = (masked == idx)  # .astype(int)
    grown = mask.copy()
    grown = ndim.morphology.binary_dilation(grown, iterations=grow)

    y, x = np.where(grown)
    if center is not None:
        x -= center[1]
        y -= center[0]
    fit = np.polyfit(x, y, 2, w=orig[grown] ** 2)
    return fit


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument(
        "input", help="Pass the filename of the output of 'mk_labels.py'")
    parser.add_argument("output")
    parser.add_argument("--grow", type=int, default=6,
                        help="Pixel count threshold for rogh lines.")
    parser.add_argument("--center", type=common.point, default=None)
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
    if len(ordered_labels) == 0:
        logging.error("There are zero labels, something must have gone wrong.")
        sys.exit(2)

    center = args.center
    lines = [make_fit(img, ordered_labels, label, args.grow, center)
             for label in range(1, int(ordered_labels.max()))]
    indata["lines"] = lines
    if center is not None:
        indata["center"] = center

    with open(args.output, "wb") as outfile:
        pickle.dump(indata, outfile)


if __name__ == "__main__":
    do()
