#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms

from chrom.plot import Plot
from chrom.filter import Filter
from chrom.options import Options
from chrom.keywords import Keywords

import util.latex as latex

DEFAULT_FILTER = {}
DEFAULT_OPTIONS = {"colorby": "channel"}
DEFAULT_PLOTKWS = {"linewidth": 0.75}

AVAILABLE_OPTIONS = {"axis": "(int, int) position of the plot.",
                     "colorby": "(string) attribute used to determine color.",
                     "scale": "(float, float) scale the plot data.",
                     "shift": "(float, float) shift the plot data.",
                     "name": "(string) name of the plot.",
                     "peaklabels": "(list) labels for peaks, from left.",
                     "smooth": "(int) smooth data with \'int\' order."}


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Plots Shimadzu chromatography data.')
    # Input / output
    parser.add_argument('infiles', nargs='+',
                        metavar='<file>[:<filter>[:<options>[:plotkws]]]',
                        help='Input files and options. '
                             'Options are scale(x|y) shift(x|y).')
    parser.add_argument('-o', '--outfile',
                        help='Output filename and format.')
    parser.add_argument('-S', '--noshow', action='store_true',
                        help='Don\'t show the image.')
    # Options
    parser.add_argument('-s', '--scale', type=float, nargs=2,
                        default=(0.9, 0.9),
                        help='The X and Y scale of the image.')
    parser.add_argument('-T', '--notex', action='store_true',
                        help='Don\'t use latex parameters.')

    parser.add_argument('--options', type=str,
                        metavar='<key>=<value>[,...]',
                        help='Options that apply to all files.')
    parser.add_argument('--filter', type=str,
                        metavar='<key>=<value>[,...]',
                        help='Filter all files.')
    parser.add_argument('--plotkws', type=str,
                        metavar='<key>=<value>[,...]',
                        help='Key and values to pass to plots.')
    # Text
    parser.add_argument('--xlabel', type=str, default='Time (\\si{\\minute})',
                        help='X-axis label.')
    parser.add_argument('--ylabel', type=str, default='Response',
                        help='Y-axis label.')
    parser.add_argument('--annotate', nargs='+',
                        metavar='<text>:<x>,<y>[:<arrow>:<x>,<y>]',
                        help='Add text to cromatogram, optional marker.')
    parser.add_argument('--legend', nargs='*', metavar='<text>[:axis]',
                        help='Add a legend with optional names.')

    args = parser.parse_args(args)

    # Update the default options

    if args.infiles is not None:
        infiles = []
        for f in args.infiles:
            infiles.append(
                Plot(f, Filter(args.filter),
                     Options(args.options, **DEFAULT_OPTIONS),
                     Keywords(args.plotkws, **DEFAULT_PLOTKWS)))
        args.infiles = infiles

    return vars(args)


def calculate_required_axes(infiles):
    nrows, ncols = 0, 0
    for f in infiles:
        if hasattr(f.options, 'axis'):
            if f.options.axis[0] > nrows:
                nrows = f.options.axis[0]
            if f.options.axis[1] > ncols:
                ncols = f.options.axis[1]
        else:
            if f.file.fileid > nrows:
                nrows = f.file.fileid
    return nrows + 1, ncols + 1


def set_shared_ylabel(ylabel, axes, figure):
    bottom, top = .1, .9
    avepos = (bottom+top)/2
    # changed from default blend (IdentityTransform(), axes[0].transAxes)
    axes[0].yaxis.label.set_transform(mtransforms.blended_transform_factory(
           mtransforms.IdentityTransform(), figure.transFigure))
    axes[0].yaxis.label.set_position((0, avepos))
    axes[0].set_ylabel(ylabel)


def main(args):
    args = parse_args(args)

    subplot_kw = {'xlabel': '', 'ylabel': '', 'xmargin': 0}
    if not args['notex']:
        latex.plot_options()

    # Calculated required axes
    fig, axes = plt.subplots(*calculate_required_axes(args['infiles']),
                             squeeze=False,
                             figsize=latex.size(*args['scale']),
                             sharex=True, sharey=True,
                             subplot_kw=subplot_kw,
                             gridspec_kw={'wspace': 0, 'hspace': 0})

    # Plot data
    for f in args['infiles']:
        f.plot(axes)

    # Cleanup axes
    for ax in axes.flatten():
        ax.ticklabel_format(axis='y', style='sci', scilimits=(-1, 3))
    for ax in axes.flatten()[1:]:
        ax.yaxis.offsetText.set_visible(False)

    # Hack for pgf not recognising none as labelcolor
    plt.xlabel(args['xlabel'])
    if args['outfile'] and args['outfile'].endswith('pgf'):
        set_shared_ylabel(args['ylabel'], axes, fig)
    else:
        fig.add_subplot(111, frameon=False)
        plt.tick_params(labelcolor='none',
                        top='off', bottom='off', left='off', right='off')
        plt.ylabel(args['ylabel'])

    # Remove uneeded withspace
    plt.tight_layout()

    # Save and/or show the output
    if args['outfile']:
        plt.savefig(args['outfile'])
    if not args['noshow']:
        plt.show()
    return


if __name__ == "__main__":
    tfile = ("/home/tom/Dropbox/Uni/Experimental/Results/"
             "20180129_eprep_apsvar/csv/005_2_006.txt")

    main([':'.join([tfile, 'mode=tic', 'colorby=event']),
          ':'.join([tfile, 'mode=mrm', 'peaklabels=[cats,bats,c,d,e,f]', 'color=#121212']),
          '--plotkws', 'linewidth=2'])
