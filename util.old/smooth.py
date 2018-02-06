import numpy as np
from scipy.interpolate import interp1d


def plot(axes, kind, num_points, *args, **kwargs):
    xs = np.array(args[0], dtype=float)
    ys = np.array(args[1], dtype=float)
    xsnew = np.linspace(xs.min(), xs.max(), num_points)
    smooth = interp1d(xs, ys, kind=kind)
    return axes.plot(xsnew, smooth(xsnew), *args[2:], **kwargs)
