import pickle
import argparse as ap

import numpy as np
import matplotlib.pyplot as plt


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument("inputs", nargs="+")
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


def compute(one, two):
    zeros_at = [- data["key_dep"][-1] / data["key_dep"][-2]
                for data in (one, two)]
    slopes = [data["slope"] for data in (one, two)]
    x = (zeros_at[1] - zeros_at[0]) / (slopes[0] - slopes[1])
    y = x * slopes[0] + zeros_at[0]
    center = np.array((y, x))
    # print("Aberration center at ({}, {})".format(x, y))
    transform_fits(one["fits"], center, 0)


def do():
    args = parse_args()
    inputs = []
    for fname in args.inputs:
        with open(fname, "rb") as infile:
            inputs.append(pickle.load(infile))
    compute(* inputs)


if __name__ == "__main__":
    do()
