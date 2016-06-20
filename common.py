# -*- coding: utf-8 -*-


import scipy as sp


def get_img(fname):
    img = sp.misc.imread(fname, True)
    img = img.astype(float)
    return img
