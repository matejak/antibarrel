# -*- coding: utf-8 -*-

# import cPickle as pickle
import pickle
import argparse as ap
import logging
import sys

import numpy as np
import scipy.ndimage as ndim

import antibarrel.common as common


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


def invert_image(image):
    image *= - 1
    image -= image.min()
    return image


def threshold_image_by_relative_value(image, relative_value=0.9):
    normed_image = image.copy() / image.max()
    if relative_value > 0:
        normed_image[normed_image < relative_value] = 0
    return normed_image


def get_labels(thresholded, num_thresh=500):
    """
    Given an image, it labels it for lines.
    It is achieved in this order:

    #. Thresholded areas are labelled.
    #. Reorder labels based on their sizes.
    #. If an area spans over less points than ``num_thresh``,
       assign a negative label value.

    Returns:
        The labelled image
    """
    labels, num = ndim.label(thresholded)
    label_counts = np.zeros(num + 1, int)
    for px in labels.flat:
        label_counts[px] += 1

    argsorted = np.argsort(label_counts)[::-1]
    label_map = np.zeros(num + 1)
    cur_min = -1
    for idx, arg in enumerate(argsorted):
        # label_counts are greater than num_thresh, but once they cease to be,
        # they are always lower and lower than the thresh.
        if label_counts[arg] < num_thresh:
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
    parser.add_argument(
        "--val-thresh", type=float, default=0.78,
        help="Initial threshold for rough lines. Use negative values "
        "to suggest that we work with negative images")
    parser.add_argument("--num-threshold", type=int, default=1000,
                        help="Pixel count threshold for rough lines.")
    parser.add_argument("--invert", action="store_true", default=False)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    img = common.get_img(args.input)
    if args.invert:
        img = invert_image(img)
    thresholded_img = threshold_image_by_relative_value(img, args.val_thresh)
    ordered_labels = get_labels(thresholded_img, args.num_threshold)
    if not ordered_labels:
        logging.error("There are zero labels, something must have gone wrong.")
        sys.exit(2)

    output = dict(
        labels=ordered_labels,
        srcim=args.input,
    )
    with open(args.output, "wb") as outfile:
        pickle.dump(output, outfile)


if __name__ == "__main__":
    main()
