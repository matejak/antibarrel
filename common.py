# -*- coding: utf-8 -*-

import numpy as np

COLORS = "bgc"


def cart2pol(y, x, center=(0, 0), norm=1):
    """
    Args:
        y
        x
        center (tuple-lik): (Y, X)

    Returns:
        tuple - :math:`(\\rho, \\varphi)`
    """
    x -= center[1]
    y -= center[0]
    rho = np.sqrt(x ** 2 + y ** 2) / norm
    phi = np.arctan2(y, x)
    return(rho, phi)


def pol2cart(rho, phi, center=(0, 0), norm=1):
    """
    Args:
        rho
        phi
        center (tuple-lik): (Y, X)

    Returns:
        np.ndarray - :math:`(y, x)`
    """
    rho *= norm
    x = rho * np.cos(phi) + center[1]
    y = rho * np.sin(phi) + center[0]
    return np.array((y, x), float)


def point(stri):
    import argparse as ap
    try:
        ret = _center2center(stri)
    except Exception as exc:
        raise ap.ArgumentTypeError(str(exc))
    return ret


def _center2center(stri):
    ret = [round(float(x)) for x in stri.split(",")]
    ret = np.array(ret, int)
    return ret


def show_points(lines, deps=None):
    if deps is not None:
        deps = ((deps[0],), (deps[1],))
    return show_points_more((lines,), deps)


def show_points_more(linelist, deplist=None):
    import matplotlib.pyplot as plt

    _, pl_quad = plt.subplots()
    _, pl_lin = plt.subplots()

    def idx2alpha(idx): return 1 - 0.8 * (idx / len(lines))

    xmin = float("inf")
    xmax = float("-inf")
    for idx, lines in enumerate(linelist):
        color = COLORS[idx]
        for idx, line in enumerate(lines):
            alpha = idx2alpha(idx)
            pl_quad.plot(line[-1], line[-3], "o" + color, alpha=alpha)
            # pl.plot(dsts, lins, "o")

            pl_lin.plot(line[-1], line[-2], "o" + color, alpha=alpha)
            # pl.plot(dsts, lins, "o")
            xmin = min(xmin, line[-1])
            xmax = max(xmax, line[-1])

    pl_quad.grid()
    pl_quad.axhline(0, color="k")
    pl_quad.set_title("Quadratic term")

    pl_lin.grid()
    pl_lin.set_title("Linear term")

    if deplist is not None:
        for idx, (dep_quad, dep_lin) in enumerate(zip(deplist[0], deplist[1])):
            color = COLORS[idx]
            dom = np.array((xmin, xmax), float)

            hom_quad = np.polyval(dep_quad, dom)
            pl_quad.plot(dom, hom_quad, color=color)
            pl_quad.set_ylim(* hom_quad)

            hom_lin = np.polyval(dep_lin, dom)
            pl_lin.plot(dom, hom_lin, color=color)
            pl_lin.set_ylim(* hom_lin)


def get_img(fname):
    import scipy.misc
    img = scipy.misc.imread(fname, True)
    img = img.astype(float)
    return img


def save_img(fname, img):
    import scipy.misc
    scipy.misc.imsave(fname, img)
