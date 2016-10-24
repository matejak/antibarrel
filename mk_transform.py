# -*- coding: utf-8 -*-

import argparse as ap

import numpy as np
import scipy.interpolate as interp

import common


class BaseRadialTform(object):
    def __init__(self, center):
        self._center = center
        self._norm = 1

    def set_norm(self, imshape):
        self._norm = float(min(imshape)) / 2.0

    def _radial_tform(self, rho):
        raise NotImplementedError()

    def __call__(self, pt):
        rho, phi = common.cart2pol(pt[0], pt[1], self._center, self._norm)
        rho_t = self._radial_tform(rho)
        pt_t = common.pol2cart(rho_t, phi, self._center, self._norm)
        return pt_t


class TformForward(BaseRadialTform):
    """
    Used to get corrected image from the distorted
    """

    def __init__(self, coeffs, center):
        super().__init__(center)
        self._exponents = np.array((4, 3, 2, 1), int)
        self._coeffs = np.array(coeffs).astype(float)

    def _radial_tform(self, rho):
        rho_t = sum(rho ** self._exponents * self._coeffs)
        return rho_t


class TformOpposite(BaseRadialTform):
    """
    Used to simulate the distortion given the image
    """

    def __init__(self, coeffs, center):
        super().__init__(center)
        self._template = np.array(
            (coeffs[0], coeffs[1], coeffs[2], coeffs[3], 0), float)

    def _radial_tform(self, rho):
        poly = self._template.copy()
        poly[-1] = - rho
        roots = np.roots(poly)
        diff = np.abs(roots - rho)
        rho_t = roots[np.argmin(diff)].real
        return rho_t


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


def do():
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
        tform_cls = TformOpposite
    else:
        tform_cls = TformForward

    dest = np.empty_like(img)
    tform = tform_cls(coeffs, center)
    tform.set_norm(dest.shape)

    for y in range(dest.shape[0]):
        for x in range(dest.shape[1]):
            dest[y, x] = get_src(interp_obj, (y, x), tform)

    common.save_img(args.output, dest)


if __name__ == "__main__":
    do()
