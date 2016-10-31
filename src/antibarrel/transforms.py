# -*- coding: utf-8 -*-
import numpy as np

import antibarrel.common


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
