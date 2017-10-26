import numpy as np


def size(wscale, hscale, textwidth=426.79135):
    inches_per_pt = 1.0 / 72.27
    golden_mean = (np.sqrt(5.0) - 1.0) / 2.0
    fig_width = textwidth * inches_per_pt * wscale  # width in inches
    fig_height = textwidth * inches_per_pt * golden_mean * hscale
    fig_size = [fig_width, fig_height]
    return fig_size
