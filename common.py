# -*- coding: utf-8 -*-


import scipy as sp


def get_img(fname):
    import scipy.misc
    img = sp.misc.imread(fname, True)
    img = img.astype(float)
    return img
