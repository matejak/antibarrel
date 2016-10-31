# -*- coding: utf-8 -*-

import argparse as ap

import numpy as np
import scipy.interpolate as interp

import antibarrel.common
import antibarrel.transforms


def get_src(src, pt, tform):
    """
    Args:
        src (2D indexable): The generalized array (supporting "float indexing")
        pt: The point of the image we would like to fill
        tform: Callable
    """
    # The dest[pt] = src[tform(pt)]
    tformed = tform(pt)
    ret = src(tformed[1], tformed[0])
    return ret


def img2interp(src):
    """
    Given a source image, return something that is interpolable
    """
    ret = interp.interp2d(
        np.arange(src.shape[1]), np.arange(src.shape[0]), src,
        bounds_error=False, fill_value=None,
    )
    return ret


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("transform",
                        help="The transformation string (a,b,c,d,cy,cx).")
    parser.add_argument("--center", type=common.point)
    parser.add_argument("--forward", action="store_true", default=False,
                        help="Make the deformation, don't compensate it.")

    parser.add_argument("output")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    """
    with open(args.input, "rb") as infile:
        indata = pickle.load(infile)
    img = common.get_img(indata["srcim"])
    """

    img = common.get_img(args.input)

    interp_obj = img2interp(img)

    in_params = args.transform.split(",")
    assert len(in_params) == 6
    coeffs = [float(x) for x in in_params[:4]]
    center = [float(x) for x in in_params[4:]]

    if args.forward:
        tform_cls = transforms.TformOpposite
    else:
        tform_cls = transforms.TformForward

    dest = np.empty_like(img)
    tform = tform_cls(coeffs, center)
    tform.set_norm(dest.shape)

    for y in range(dest.shape[0]):
        for x in range(dest.shape[1]):
            dest[y, x] = get_src(interp_obj, (y, x), tform)

    common.save_img(args.output, dest)


if __name__ == "__main__":
    main()
