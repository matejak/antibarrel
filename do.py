# import cPickle as pickle
import pickle
import argparse as ap

import numpy as np
import scipy as sp
import scipy.ndimage as ndim
import scipy.optimize as opt
import matplotlib.pyplot as plt
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


def get_lines(img, num_thresh=500, val_thresh=0.6):
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
    labels = label_map[labels]
    return labels


def make_fit(orig, masked, idx):
    mask = (masked == idx)  # .astype(int)
    grown = mask.copy()
    for ii in range(4):
        grown = ndim.morphology.binary_dilation(grown)

    y, x = np.where(grown)
    fit = np.polyfit(x, y, 2, w=orig[grown] ** 2)
    return fit


def residue_x(coeffs, x, y):
    lin, x0 = coeffs
    ret = y - (x0 + lin * x)
    return ret


def preclean_data(xs, ys):
    hi = np.percentile(ys, 80)
    lo = np.percentile(ys, 20)
    span = hi - lo
    bound_lo = lo - span
    bound_hi = hi + span
    is_ok = (bound_lo < ys) * (ys < bound_hi)
    return xs[is_ok], ys[is_ok]


def robust_fit(xs, ys, fsc=1e-6):
    xs, ys = preclean_data(xs, ys)
    res_robust = opt.least_squares(residue_x, np.zeros(2), method="dogbox", x_scale=1e-9,
                                   loss='arctan', f_scale=fsc, args=(xs, ys), verbose=0, ftol=1e-12)
    return res_robust


def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output", nargs="?")
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    return args


def get_img(fname):
    img = sp.misc.imread(fname, True)
    img = img.astype(float)
    return img


def get_result(img):
    ordered_labels = get_lines(img)

    rotim = img

    lines = [make_fit(rotim, ordered_labels, label)
             for label in range(1, int(ordered_labels.max()))]

    quads, lins, dsts = [np.array(x) for x in zip(* lines)]
    fit = robust_fit(dsts, quads)["x"]

    lines_out = (quads, lins, dsts)
    key_dep = fit

    output = dict(
        fits=np.array(lines),
        slope=np.median(lins),
        lines_out=lines_out,
        key_dep=key_dep,
    )
    return output


def plot_result(rotim, output):
    quads, lins, dsts = output["lines_out"]
    fit = output["key_dep"]

    xp = np.linspace(0, rotim.shape[1], 200)

    fig, pl = plt.subplots()
    x, y = preclean_data(dsts, quads)
    pl.plot(x, y, "o")
    # pl.plot(dsts, lins, "o")

    pl.plot(x, np.poly1d(fit)(x))

    pl.grid()

    ordered_labels = get_lines(rotim)
    polys = []
    for idx in range(23, 28):
        fit = make_fit(rotim, ordered_labels, idx)
        poly = np.poly1d(fit)
        polys.append((poly, fit[0]))

    fig, pl = plt.subplots()
    pl.imshow(rotim, cmap=plt.cm.gray)
    for poly, label in polys:
        pl.plot(xp, poly(xp), label="a = %.02g" % (label * 1e6))
    pl.legend()

    plt.show()


def do():
    args = parse_args()
    img = get_img(args.input)
    output = get_result(img)
    if args.output is not None:
        with open(args.output, "wb") as outfile:
            pickle.dump(output, outfile)
    if args.plot:
        plot_result(img, output)


if __name__ == "__main__":
    do()
