# -*- coding: utf-8 -*-

import pickle
import argparse as ap

import numpy as np
import scipy.ndimage as ndim
import matplotlib.pyplot as plt


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument("inputs", nargs=2)
    parser.add_argument("output")
    args = parser.parse_args()
    return args


def transform_fits(fits, center, slope):
    regu = fits[:, -2] - np.median(fits[:, -2])
    dom = fits[:, -1].copy()
    fig, pl = plt.subplots()
    pl.plot(dom, regu, "o")

    # first shift by center
    # y = a * x^2 + b * x + c
    # vvv new vector
    #  t = (x, y) - (cx, cy)
    #  orig ^^^^      ^^^^ center (i.e. shift) vector
    for fit in fits:
        # a stays the same
        # c => a * cx^2 + b * cx - cy
        # new c depends on the OLD b, so we do b last.
        fit[-1] += center[1] * (fit[-3] * center[1] + fit[-2]) - center[0]
        # b => 2 * a * cx + b
        fit[-2] += 2 * fit[-3] * center[1]
    # Then rotate according to slope
    # Won't work -- rotating a parabolla is not a pb any more

    regu = fits[:, -2] - np.median(fits[:, -2])
    pl.plot(dom, regu, "o")
    pl.grid()

    plt.show()


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


def compute(one, two):
    """
    zeros_at = [- data["key_dep"][-1] / data["key_dep"][-2]
                for data in (one, two)]
    slopes = [data["slope"] for data in (one, two)]
    """
    zeros_at = [np.roots(data["key_dep"])[0]
                for data in (one, two)]
    slopes = [np.polyval(data["key_lin"], zero)
              for data, zero in zip((one, two), zeros_at)]
    # assuming y = b * x + c,
    # Essentially Dc / Db
    x = (zeros_at[1] - zeros_at[0]) / (slopes[0] - slopes[1])
    y = x * slopes[0] + zeros_at[0]
    center = np.array((y, x))
    center = np.round(center).astype(int)
    print("Aberration center at ({}, {})".format(* center))

    rotateds = [rot2center(data["image"], np.rad2deg(np.arctan(slope)), center)
                for data, slope in zip((one, two), slopes)]

    # fig, pl = plt.subplots()
    # pl.imshow(rotateds[1], cmap=plt.cm.gray)
    # pl.plot(center[1], center[0], "or")

    # transform_fits(one["fits"], center, 0)
    return center, rotateds


def do():
    args = parse_args()
    inputs = []
    for fname in args.inputs:
        with open(fname, "rb") as infile:
            inputs.append(pickle.load(infile))
    center, rotated = compute(* inputs)
    output = dict(
        center=center,
        rotated=rotated
    )
    with open(args.output, "wb") as outfile:
        pickle.dump(output, outfile)


if __name__ == "__main__":
    do()
