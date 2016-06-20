# -*- coding: utf-8 -*-

# import cPickle as pickle
import pickle
import argparse as ap

import numpy as np
import scipy.ndimage as ndim
import matplotlib.pyplot as plt

import common


"""
We detect lines in the images.
The method is this:

#. Threshold the image (i.e. greater or lower than ``val_thresh`` 0.6 of its max)
#. Label the regions (create a label array)
#. Set the labels in this way:

    * 0, 1, 2, ...: Areas that have more than num_thresh values, the label is inversely proportional to the area size.
      Therefore, it is likely that 0 will be the background index.
    * -1, -2, ...: Areas below the threshold, the decrease of labels is proportional to decrease of the area size

#. Fit a line nicely to determine the rotation.
#. Rotate the image so lines are roughly horizontal.
#. Repeat thresholding--labelling.
#. Calculate the 2nd degree-polynomial fits to "big" lines, capture correlation of first two coefficients on the third (constant) one.
#. Fit a linear dependence of each of the first two coeffs on the third one.

"""


def get_lines(img, num_thresh=500, val_thresh=0.6):
    """
    Given an image, it labels it for lines.
    It is achieved in this order:

    #. The image is thresholded using :param:`val_thresh`.
    #. Thresholded areas are labelled.
    #. Reorder labels based on their sizes.
    #. If an area spans over less points than :param:`num_thresh`,
       assign a negative label value.

    Returns:
        The labelled image
    """
    low = img.copy()
    low /= low.max()
    low[low < val_thresh] = 0

    labels, num = ndim.label(low)
    nums = np.zeros(num + 1, int)
    for px in labels.flat:
        nums[px] += 1

    argsorted = np.argsort(nums)[::-1]
    label_map = np.zeros(num + 1)
    cur_min = -1
    for idx, arg in enumerate(argsorted):
        # nums are greater than num_thresh, but once they cease to be,
        # they are always lower and lower than the thresh.
        if nums[arg] < num_thresh:
            idx = cur_min
            cur_min -= 1
        label_map[arg] = idx
    # this is the labels reordering
    labels = label_map[labels]
    return labels


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--val-threshold", type=float, default=0.5,
                        help="Initial threshold for rough lines.")
    parser.add_argument("--num-threshold", type=int, default=1000,
                        help="Pixel count threshold for rogh lines.")
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    return args


def do():
    args = parse_args()
    img = common.get_img(args.input)
    ordered_labels = get_lines(img, args.num_threshold, args.val_threshold)
    output = dict(
        labels=ordered_labels,
        srcim=args.input,
    )
    with open(args.output, "wb") as outfile:
        pickle.dump(output, outfile)


if __name__ == "__main__":
    do()
