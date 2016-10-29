# -*- coding: utf-8 -*-
import numpy as np


def _plot_dep(plt, func):
    _max = 1.8
    dom = np.linspace(0, _max, 200)
    linear = dom.copy()
    ours = func(dom)
    plt.plot(dom, linear, "--", label="no distortion")
    plt.plot(dom, ours, "-", label="distortion")
    plt.set_xlim(0, _max)
    plt.set_ylim(0, _max)

    plt.set_xlabel("real radius / a.u.")
    plt.set_ylabel("measured radius / a.u.")
    return dom
