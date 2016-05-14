# -*- coding: utf-8 -*-

# import cPickle as pickle
import pickle
import argparse as ap

import numpy as np
import scipy as sp
import scipy.ndimage as ndim
import scipy.optimize as opt
import matplotlib.pyplot as plt

import statsmodels.formula.api as sfapi
# import skimage as si
# import skimage.measure


"""
We detect lines in the images.
The method is this:

#. Threshold the image (i.e. greater or lower than ``val_thresh`` 0.6 of its max)
#. Label the regions (create a label array)
#. Set the labels in this way:

    * 0, 1, 2, ...: Areas that have more than num_thresh values, the label is inversely proportional to the area size.
      Therefore, it is likely that 0 will be the background index.
    * -1, -2, ...: Areas below the threshold, the decrease of labels is proportional to decrease of the area size

#. Fit a line nicely to determine the rotation.
#. Rotate the image so lines are roughly horizontal.
#. Repeat thresholding--labelling.
#. Calculate the 2nd degree-polynomial fits to "big" lines, capture correlation of first two coefficients on the third (constant) one.
#. Fit a linear dependence of each of the first two coeffs on the third one.

"""


def get_lines(img, num_thresh=500, val_thresh=0.6, inspect=False):
    """
    Given an image, it labels it for lines.
    It is achieved in this order:

    #. The image is thresholded using :param:`val_thresh`.
    #. Thresholded areas are labelled.
    #. Reorder labels based on their sizes.
    #. If an area spans over less points than :param:`num_thresh`,
       assign a negative label value.

    Returns:
        The labelled image
    """
    low = img.copy()
    low /= low.max()
    low[low < val_thresh] = 0

    labels, num = ndim.label(low)
    nums = np.zeros(num + 1, int)
    for px in labels.flat:
        nums[px] += 1

    argsorted = np.argsort(nums)[::-1]
    label_map = np.zeros(num + 1)
    cur_min = -1
    for idx, arg in enumerate(argsorted):
        # nums are greater than num_thresh, but once they cease to be,
        # they are always lower and lower than the thresh.
        if nums[arg] < num_thresh:
            idx = cur_min
            cur_min -= 1
        label_map[arg] = idx
    # this is the labels reordering
    labels = label_map[labels]
    if inspect:
        fig, pl = plt.subplots()
        plo = pl.imshow(labels, vmin=1)
        fig.colorbar(plo)
        plt.show()
    return labels


def make_fit(orig, masked, idx, center=None, grow=6):
    """
    Given original array, the labelled one, label and positionss of the
    zero coordinate, return a polynomial fit for hte respective line.
    """
    mask = (masked == idx)  # .astype(int)
    grown = mask.copy()
    grown = ndim.morphology.binary_dilation(grown, iterations=grow)
    if 0:
        _, pl = plt.subplots()
        base = mask.copy().astype(float)
        base += grown.copy().astype(float)
        base += orig / orig.max()
        pl.imshow(base)
        plt.show()

    y, x = np.where(grown)
    if center is not None:
        x -= center[1]
        y -= center[0]
    fit = np.polyfit(x, y, 2, w=orig[grown] ** 2)
    return fit


def residue_x(coeffs, x, y):
    lin, x0 = coeffs
    ret = y - (x0 + lin * x)
    return ret


def preclean_rough(xs, ys):
    hi = np.percentile(ys, 80)
    lo = np.percentile(ys, 20)
    span = hi - lo
    bound_lo = lo - span
    bound_hi = hi + span
    is_ok = (bound_lo < ys) * (ys < bound_hi)
    return xs[is_ok], ys[is_ok]


def robust_fit(xs, ys):
    xs, ys = preclean_data(xs, ys)
    res_robust = opt.least_squares(residue_x, np.zeros(2), method="dogbox",
                                   loss='arctan', args=(xs, ys), verbose=0)
    return res_robust["x"]


def preclean_data(xs, ys):
    norig = len(xs)
    xs, ys = preclean_rough(xs, ys)
    for _ in range(3):
        regression = sfapi.ols("data ~ x", data=dict(data=ys, x=xs)).fit()

        test = regression.outlier_test()
        # The greater t is, the more outliers there will be
        # print(test.iloc[:, 2])
        selection = [i for i, t in enumerate(test.iloc[:, 1]) if t > 0.15]
        selection = np.array(selection, int)

        xs = xs[selection]
        ys = ys[selection]

    noutliers = norig - len(xs)
    print("Removed total {} outliers".format(noutliers))

    """
    import statsmodels.api
    import statsmodels.graphics as smgraphics

    figure = smgraphics.regressionplots.plot_fit(regression, 1)
    smgraphics.regressionplots.abline_plot(
        model_results=regression, ax=figure.axes[0])
    """

    return xs, ys


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output", nargs="?")
    parser.add_argument("--plot", action="store_true")
    parser.add_argument("--inspect", action="store_true")
    args = parser.parse_args()
    return args


def get_img(fname):
    img = sp.misc.imread(fname, True)
    img = img.astype(float)
    return img


def get_result(img, center=None, inspect=False):
    ordered_labels = get_lines(img, val_thresh=0.5, num_thresh=1000, inspect=inspect)

    lines = [make_fit(img, ordered_labels, label, center)
             for label in range(1, int(ordered_labels.max()))]

    quads, lins, dsts = [np.array(x) for x in zip(* lines)]
    fit = robust_fit(dsts, quads)
    key_dep = fit

    fit = robust_fit(dsts, lins)
    key_lin = fit

    lines_out = (quads, lins, dsts)

    output = dict(
        image=img,
        fits=np.array(lines),
        lines_out=lines_out,
        key_dep=key_dep,
        key_lin=key_lin,
    )
    return output


def plot_result(* outputs):
    _, pl_quad = plt.subplots()
    _, pl_lin = plt.subplots()
    for idx, output in enumerate(outputs):
        quads, lins, dsts = output["lines_out"]
        fit = output["key_dep"]
        img = output["image"]

        xp = np.linspace(0, img.shape[1], 200)

        x, y = preclean_rough(dsts, quads)
        pl_quad.plot(x, y, "o")
        # pl.plot(dsts, lins, "o")

        pl_quad.axhline(0, color="k")
        pl_quad.plot(x, np.poly1d(fit)(x),
                     label="{} = {:.3g}".format(idx, fit[-2]))
        pl_quad.set_title("Quadratic term")

        fit = output["key_lin"]
        x, y = preclean_rough(dsts, lins)
        pl_lin.plot(x, y, "o")
        # pl.plot(dsts, lins, "o")

        pl_lin.plot(x, np.poly1d(fit)(x),
                    label="{} = {:.3g}".format(idx, fit[-2]))
        pl_lin.set_title("Linear term")

        ordered_labels = get_lines(img)
        polys = []
        for idx in range(10, 30, 4):
            fit = make_fit(img, ordered_labels, idx)
            poly = np.poly1d(fit)
            polys.append((poly, fit[-3]))

        fig, pl = plt.subplots()
        pl.imshow(img, cmap=plt.cm.gray)
        for poly, label in polys:
            pl.plot(xp, poly(xp), label="a = %.02g" % (label * 1e6))
        pl.legend()

    pl_quad.grid()
    pl_quad.legend()
    pl_lin.grid()
    pl_lin.legend()
    plt.show()


def do():
    args = parse_args()
    img = get_img(args.input)
    output = get_result(img, inspect=args.inspect)
    if args.output is not None:
        with open(args.output, "wb") as outfile:
            pickle.dump(output, outfile)
    if args.plot:
        plot_result(output)


if __name__ == "__main__":
    do()
