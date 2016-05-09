import numpy as np


def cart2pol(pt):
    x, y = pt
    rho = np.sqrt(x ** 2 + y ** 2)
    phi = np.arctan2(y, x)
    return(rho, phi)


def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return np.array((x, y), float)


def _row2val(vals, rho, ycf):
    ys = np.ones(4) * y
    for idx in range(3):
        ys[:(-idx - 1)] *= y
    # ^^^ should result in
    # ^^^ y^4, y^3, y^2, y
    ret = 0
    ret -= rho
    for val, idx in enumerate(vals):
        ret += vals[idx] * val * ys[idx]
    return ret


# vals: a, b, c, d, + n-times y0
# matrix row: R, cf, idx
def _vals2val(vals, matrix):
    fun = 0
    for row in matrix:
        fun += _row2val(vals[:4], row[0], vals[4 + int(row[2])] * row[1])


def formulate(fit_quad, center):
    ylim, xlim = center
    polys = [(fit_quad(const), 0, const)
             for const in np.linspace(ylim / 3,  ylim, 5)]
    # a, b, c, d + n-times y0
    n_unks = 4 + len(polys)
    PTS_IN_POLY = 5
    result = np.zeros(n_unks, float)
    result[3] = 1
    # defaults are a, b, c, d
    #           == 0, 0, 0, 1
    data = np.zeros((PTS_IN_POLY * len(polys), 3))

    ptidx = 0
    for poly in polys:
        points = np.polyval(poly, np.linspace(xlim / 3, xlim, PTS_IN_POLY))
        for pt in points:
            rho, phi = cart2pol(pt - center)
            cphi = np.cos(phi)
            rhs[ptidx] = rho
            result[:4] = 1 / cphi
