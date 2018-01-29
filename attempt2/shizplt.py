#!/usr/bin/env python3

import argparse
import re

# Input files into an array

# Make a class for data
# filename
# options

class ChromPlotOptions(object):
    """Stores per-file options for plotting.
    """
    def __init__(self, name=None, axis=None,
                 scale=[1.0, 1.0], shift=[0.0, 0.0]):
        self.name = name
        self.axis = None
        self.scale = scale
        self.shift = shift

    def parse(self, string: str):
        """Format is <filename>[:<option>=<value>[,...]]
        Valid options are axis, name, scale ((x, y)), shift ((x, y))."""
        # Clean up input
        string = string.strip().replace(' ', '').lower()

        tokens = re.split('\,(?![\d\.]*[\)\]])', string)

        for token in tokens:
            key, val = token.split('=')
            if key == 'name':
                self.name = val
            elif key == 'axis':
                self.axis = int(val)
            elif key == 'scale':
                self.scale = [float(x) for x in
                              val.strip('[]').split(',')]
            elif key == 'shift':
                self.shift = [float(x) for x in
                              val.strip('[]').split(',')]


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
    parser.add_argument('-f', '--filter', type=str,
                        help='Filter data before plotting.')
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
        for arg in args.infile:
            options = {"scalex": None, "scaley": None,
                       "shiftx": None, "shifty": None}
            tokens = re.split(':', arg)
            if len(tokens) > 1:
                # parser.error('Invalid format for infile ' + arg)
                for token in tokens[1:]:
                    option, value = re.split(',', token)
                    options[option] = value
            infiles.append([tokens[0], options])
        args.infile = infiles

    if args.filter is not None:
        args.filter = filters.parse(args.filter)
    if args.smooth is not None:
        if len(args.smooth) == 0:
            args.smooth = ['cubic', 300]
        elif len(args.smooth) == 1:
            args.smooth.append(300)
        elif len(args.smooth) > 2:
            parser.error('Specify 1 or 2 arguments.')
    if args.annotate is not None:
        annotations = []
        for arg in args.annotate:
            tokens = re.split(':|,', arg)
            if len(tokens) % 3 != 0:
                parser.error('Invalid annotation format for ' + arg)
            annotations.append(tokens)
        args.annotate = annotations
    if args.labelpeaks is not None:
            args.labelpeaks = filters.parse(args.labelpeaks)
    if args.legend is not None:
            args.legend = filters.parse(args.legend)
    # if args.shift is not None:
    #     args.shift = parse_filter(parser, args.shift)
    return vars(args)

def main(args):

