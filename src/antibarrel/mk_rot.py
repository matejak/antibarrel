# -*- coding: utf-8 -*-

# import cPickle as pickle
import pickle
import argparse as ap

import numpy as np
import scipy.ndimage as ndim

import antibarrel.common as common


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--center", type=common.point)

    parser.add_argument("output")
    args = parser.parse_args()
    return args


def rot2center(what, angle, center=None):
    pivot = center
    if pivot is None:
        pivot = np.array(center) // 2
    # Taken from
    # http://stackoverflow.com/questions/25458442/rotate-a-2d-image-around-specified-origin-in-python
    padX = [what.shape[1] - pivot[0], pivot[0]]
    padY = [what.shape[0] - pivot[1], pivot[1]]
    imgP = np.pad(what, [padY, padX], 'constant')
    imgR = ndim.rotate(imgP, angle, reshape=False)
    return imgR[padY[0]:- padY[1], padX[0]:- padX[1]]


def main():
    args = parse_args()
    with open(args.input, "rb") as infile:
        indata = pickle.load(infile)

    img = common.get_img(indata["srcim"])
    angle = np.rad2deg(np.arctan(indata["slope"]))
    rotated = rot2center(img, angle, args.center)

    common.save_img(args.output, rotated)


if __name__ == "__main__":
    main()
