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

    deps = [np.array(outp["key_dep"])
            for outp in outputs]
    fusion = dict(
        center=indata["center"],
        key_deps=np.array(deps),
    )

    if args.output is not None:
        with open(args.output, "wb") as outfile:
            pickle.dump(fusion, outfile)
    if args.plot:
        do.plot_result(outputs[0], outputs[1])


if __name__ == "__main__":
    main()
