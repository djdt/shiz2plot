import numpy
import matplotlib.pyplot as plt

# Defines requires for latex
plt.rc('text', usetex=True)
plt.rc('pgf', rcfonts=False)
plt.rcParams['text.latex.preamble'] = ['\\usepackage{siunitx}']
plt.rcParams['pgf.preamble'] = ['\\usepackage{siunitx}',
                                '\\sisetup{detect-all, math-rm=\\mathsf}']


def size(wscale, hscale, textwidth=426.79135):
    inches_per_pt = 1.0 / 72.27
    golden_mean = (numpy.sqrt(5.0) - 1.0) / 2.0
    fig_width = textwidth * inches_per_pt * wscale  # width in inches
    fig_height = textwidth * inches_per_pt * golden_mean * hscale
    fig_size = [fig_width, fig_height]
    return fig_size
