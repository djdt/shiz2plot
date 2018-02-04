#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt

import cplot
from cfilter import Filter
from coptions import Options
from ckeywords import Keywords

import latex

DEFAULT_FILTER = {}
DEFAULT_OPTIONS = {"axis": None, "colorby": "channel",
                   "scale": (1., 1.), "shift": (0., 0.)}
DEFAULT_PLOTKWS = {"linewidth": 0.75}


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
    parser.add_argument('--annotate', nargs='+',
                        metavar='<text>:<x>,<y>[:<arrow>:<x>,<y>]',
                        help='Add text to cromatogram, optional marker.')
    # parser.add_argument('--labelpeaks', nargs='+',
    #                     metavar='<label>[:<filter>]',
    #                     help='Label largest peak in filter.')
    # parser.add_argument('--legend', nargs='*', metavar='<text>[:<filer>]',
    #                     help='Add a legend with optional names.')
    # Processing
    # parser.add_argument('--detectpeaks', nargs='+',
    #                     metavar='<filter>',
    #                     help='Detect peaks for labelling.')
    # parser.add_argument('--smooth', nargs='*', metavar='<kind> <num>',
    #                     help='Interpolate and smooth plots.')

    args = parser.parse_args(args)

    # Update the default options

    if args.infiles is not None:
        infiles = []
        for f in args.infiles:
            infiles.append(
                cplot.Plot(f, Filter(args.filter),
                           Options(args.options, **DEFAULT_OPTIONS),
                           Keywords(args.plotkws, **DEFAULT_PLOTKWS)))
        args.infiles = infiles

    # for f in args.infiles:
    #     # Update given options
    #     if args.filter is not None:
    #         f.filter.parse(args.filter, overwrite=False)
    #     if args.options is not None:
    #         f.options.parse(args.options, overwrite=False)
    #     if args.plotkws is not None:
    #         f.plotkws.parse(args.plotkws, overwrite=False)

    # if args.smooth is not None:
    #     if len(args.smooth) == 0:
    #         args.smooth = ['cubic', 300]
    #     elif len(args.smooth) == 1:
    #         args.smooth.append(300)
    #     elif len(args.smooth) > 2:
    #         parser.error('Specify 1 or 2 arguments.')
    # if args.annotate is not None:
    #     annotations = []
    #     for arg in args.annotate:
    #         tokens = re.split(':|,', arg)
    #         if len(tokens) % 3 != 0:
    #             parser.error('Invalid annotation format for ' + arg)
    #         annotations.append(tokens)
    #     args.annotate = annotations
    # if args.labelpeaks is not None:
    #         args.labelpeaks = filters.parse(args.labelpeaks)
    # if args.legend is not None:
    #         args.legend = filters.parse(args.legend)
    return vars(args)


def calculate_required_axes(infiles):
    nrows, ncols = 0, 0
    for f in infiles:
        if f.options.axis[0] > nrows:
            nrows = f.options.axis[0]
        if f.options.axis[1] > ncols:
            ncols = f.options.axis[1]
    return nrows + 1, ncols + 1


def annotate(text, ax):
    ax.annotate(text,
                xy=(1, 1), xycoords='axes fraction',
                xytext=(-5, -5), textcoords='offset points',
                fontsize=10, ha='right', va='top')


def main(args):
    args = parse_args(args)

    # Calculated required axes

    subplot_kw = {'xlabel': '', 'ylabel': '', 'xmargin': 0}
    fig, axes = plt.subplots(*calculate_required_axes(args['infiles']),
                             squeeze=False,
                             figsize=latex.size(*args['scale']),
                             sharex=True, sharey=True,
                             subplot_kw=subplot_kw,
                             gridspec_kw={'wspace': 0, 'hspace': 0})

    for f in args['infiles']:
        f.plot(axes)

    plt.show()
    return


if __name__ == "__main__":
    tfile = ("/home/tom/Dropbox/Uni/Experimental/Results/"
             "20180129_eprep_apsvar/csv/005_2_006.txt")

    main([':'.join([tfile, 'mode=tic', 'colorby=event']),
          ':'.join([tfile, 'mode=mrm']),])
