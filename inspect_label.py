# -*- coding: utf-8 -*-

# import cPickle as pickle
import pickle
import argparse as ap

import numpy as np
import scipy.ndimage as ndim
import matplotlib.pyplot as plt

import common


def show(im, labels):
    fig, pl = plt.subplots()
    pl.imshow(im, cmap=plt.cm.gray)
    plo = pl.imshow(labels, vmin=1)
    fig.colorbar(plo)
    plt.show()
