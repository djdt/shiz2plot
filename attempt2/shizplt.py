#!/usr/bin/env python3

import argparse
import chrom

# Input files into an array

# Make a class for data
# filename
# options


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Plots Shimadzu chromatography data.')
    # Input / output
    parser.add_argument('infiles', nargs='+',
                        metavar='<file>[:<option>,<value>]',
                        help='Input files and options. '
                             'Options are scale(x|y) shift(x|y).')
    parser.add_argument('-o', '--outfile',
                        help='Output filename and format.')
    parser.add_argument('-S', '--noshow', action='store_true',
                        help='Don\'t show the image.')
    parser.add_argument('--overlay', action='store_true',
                        help='Overlay the images.')
    # Options
    parser.add_argument('-s', '--scale', type=float, nargs=2,
                        default=(0.9, 0.9),
                        help='The X and Y scale of the image.')
    parser.add_argument('-k', '--keyword', nargs='+', action='append',
                        help='Key and values to pass to subplots.')
    parser.add_argument('-K', '--plotkeyword', nargs='+', action='append',
                        help='Key and values to pass to plot.')
    # parser.add_argument('--colors', nargs='+',
    #                     help='Colors for the plot.')
    # parser.add_argument('--colorby', default='channel',
    #                     choices=['channel', 'event', 'file', 'trace'],
    #                     help='How the traces are colored.')
    # parser.add_argument('--names', nargs='*',
    #                     help='The names of the subplots.')
    # Filtering
    parser.add_argument('--options', type=str,
                        help='Options that apply to all files.')
    parser.add_argument('--filter', type=str,
                        help='Filter all files.')
    # Text
    # parser.add_argument('--annotate', nargs='+',
    #                     metavar='<text>:<x>,<y>[:<arrow>:<x>,<y>]',
    #                     help='Add text to cromatogram, optional marker.')
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
    if args.infile is not None:
        infiles = []
        for f in args.infiles:
            infiles.append(chrom.Plot(f))
        args.infile = infiles

    if args.options is not None:
        args.options = chrom.Options(args.options)
    if args.filter is not None:
        args.filter = chrom.Filter(args.filter)
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
    # if args.shift is not None:
    #     args.shift = parse_filter(parser, args.shift)
    return vars(args)


def main(args):
    args = parse_args(args)

    return
    # Create a list of files

if __name__ == "__main__":
    tfile = "/home/tom/Dropbox/Uni/Experimental/Results/20180129_eprep_apsvar/csv/005_2_006.txt"
    toptions = ""
    tfilter = "type=tic,event=3"

    tstring = ":".join([tfile, toptions, tfilter])
    print("tstring:", tstring)

    plt = chrom.Plot(tstring)

    print(plt.__dict__)

    for trace in plt.get_traces():
        print(trace.event)

    main('test ' + tfile)
