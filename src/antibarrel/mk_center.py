# -*- coding: utf-8 -*-

import pickle
import argparse as ap

import numpy as np


def compute(one, two):
    zeros_at = [data["zero_at"]
                for data in (one, two)]
    slopes = [data["slope"]
              for data in (one, two)]
    # assuming y = b * x + c,
    # vvv is essentially Dc / Db
    x = (zeros_at[1] - zeros_at[0]) / (slopes[0] - slopes[1])
    y = x * slopes[0] + zeros_at[0]
    center = np.array((y, x))
    center = np.round(center).astype(int)

    return center


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument("input", nargs="+",
                        help="The deps pickles.")
    parser.add_argument("output")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    indata = []
    for fname in args.input:
        with open(fname, "rb") as infile:
            indata.append(pickle.load(infile))

    center = compute(* indata)
    output = "{:f},{:f}".format(center[0], center[1])

    with open(args.output, "w") as outfile:
        outfile.write(output)


if __name__ == "__main__":
    main()
