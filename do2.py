# -*- coding: utf-8 -*-

# import cPickle as pickle
import pickle
import argparse as ap

import numpy as np
import scipy as sp
import do


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output", nargs="?")
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    with open(args.input, "rb") as infile:
        indata = pickle.load(infile)
    imgs = indata["rotated"]

    outputs = [do.get_result(img, indata["center"])
               for img in imgs]

    if args.output is not None:
        with open(args.output, "wb") as outfile:
            pickle.dump(outputs, outfile)
    if args.plot:
        do.plot_result(outputs[0])
        do.plot_result(outputs[1])


if __name__ == "__main__":
    main()
