#!/usr/bin/python3

import argparse
import re
import sys

import matplotlib.pyplot as plt
import numpy as np

from parsers import shiz, thermo, waters
from util import colors, filters, latex, smooth, plotfuncs

plt.rc('text', usetex=True)
plt.rc('pgf', rcfonts=False)
plt.rcParams['text.latex.preamble'] = ['\\usepackage{siunitx}']
plt.rcParams['pgf.preamble'] = ['\\usepackage{siunitx}',
                                '\\sisetup{detect-all, math-rm=\\mathsf}']

base16_colors = ['#4271ae', '#f5871f', '#c82829',
                 '#8959a8', '#eab700', '#718c00', '#3e999f']


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Plots chromatography data.',
        epilog='Filters are formatted as a stting of options and numbers. '
               'Options are: f[ile] e[vent] c[hannel] t[ype] '
               'precursor product. '
               'for type options 0=tic, 1=mrm. An example filter: f1t0c0')
    # Input / output
    parser.add_argument('infile', nargs='+',
                        metavar='<file>[:<option>,<value>]',
                        help='Input files and options. '
                             'Options are scale(x|y) shift(x|y).')
    # parser.add_argument('-f', '--format', default='shimadzu',
    #                     choices=['shimadzu', 'waters', 'thermo'],
    #                     help='Input file format.')
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
    parser.add_argument('--colors', nargs='+',
                        help='Colors for the plot.')
    parser.add_argument('--colorby', default='channel',
                        choices=['channel', 'event', 'file', 'trace'],
                        help='How the traces are colored.')
    parser.add_argument('--names', nargs='*',
                        help='The names of the subplots.')
    # Filtering
    parser.add_argument('-e', '--events', type=int, nargs='+',
                        help='Events to plot.')
    parser.add_argument('-c', '--channels', type=int, nargs='+',
                        help='Channels to plot.')
    parser.add_argument('-p', '--precursors', type=float, nargs='+',
                        help='precursor ions to plot.')
    parser.add_argument('-d', '--products', type=float, nargs='+',
                        help='product ions to plot.')
    parser.add_argument('-t', '--type', choices=['tic', 'mrm'], nargs='+',
                        default=['tic', 'mrm'],
                        help='Show event of these types.')
    # Text
    parser.add_argument('--annotate', nargs='+',
                        metavar='<text>:<x>,<y>[:<arrow>:<x>,<y>]',
                        help='Add text to cromatogram, optional marker.')
    parser.add_argument('--labelpeaks', nargs='+',
                        metavar='<label>[:<filter>]',
                        help='Label largest peak in filter.')
    parser.add_argument('--legend', nargs='*', metavar='<text>[:<filer>]',
                        help='Add a legend with optional names.')
    # Processing
    # parser.add_argument('--shift', nargs='+', metavar='<shift>[:<filter>]',
    #                     help='Shift traces along x axis.')
    parser.add_argument('--detectpeaks', nargs='+',
                        metavar='<filter>',
                        help='Detect peaks for labelling.')
    parser.add_argument('--smooth', nargs='*', metavar='<kind> <num>',
                        help='Interpolate and smooth plots.')

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


args = parse_args(sys.argv[1:])

# Setup colors
colors = colors.get_colors('base16', args['colors'])

# Setup limits and labels
xlabel = 'Time (\\si{\\minute})'
ylabel = 'Response'

subplot_kw = {'xlabel': '', 'ylabel': '', 'xmargin': 0}
plot_kw = {'linewidth': 0.75}
if args['keyword']:
    for keyword in args['keyword']:
        key = keyword[0]
        val = keyword[1:]

        if key == 'xlabel':
            xlabel = val[0]
        elif key == 'ylabel':
            ylabel = val[0]
        elif len(val) == 1:
            subplot_kw[key] = val[0]
        elif key == 'xticks' or key == 'yticks':
            subplot_kw[key] = np.arange(*[float(x) for x in val])
        else:
            subplot_kw[key] = [float(x) for x in val]

if args['plotkeyword']:
    for keyword in args['plotkeyword']:
        key = keyword[0]
        val = keyword[1:]
        if key == 'linewidth' or 'lw':
            plot_kw['linewidth'] = float(val[0])


fig, axes = plt.subplots(1 if args['overlay'] else len(args['infile']),
                         figsize=latex.size(*args['scale']),
                         sharex=True, sharey=True,
                         subplot_kw=subplot_kw,
                         gridspec_kw={'wspace': 0, 'hspace': 0})

if len(args['infile']) == 1:
    axes = [axes]
elif args['overlay']:
    axes = [axes for x in args['infile']]

total_plotted = 0
handles = []
for i, (ax, (f, options)) in enumerate(zip(axes, args['infile'])):
    # Detemine file format
    file_format = None
    with open(f) as fp:
        for l in range(10):
            line = fp.readline()
            if 'LabSolutions' in line:
                file_format = 'shimadzu'
                break
            elif 'Chromeleon' in line:
                file_format = 'thermo'
                break
        fp.close()
    # Parse input file
    if file_format == 'shimadzu':
        data = shiz.parse(f, i)
    elif file_format == 'thermo':
        data = thermo.parse(f, i)
    elif file_format == 'waters':
        data = waters.parse(f, i)
    else:
        print('Unsupported file format')
        sys.exit(1)

    # Plot the data
    plotted = 0
    for ev in data['traces']:
        # Filter out unwanted data
        if args['events'] and ev['event'] not in args['events']:
            continue
        if args['channels'] and ev['channel'] not in args['channels']:
            continue
        if args['precursors'] and ev['precursor'] not in args['precursors']:
            continue
        if args['products'] and ev['product'] not in args['products']:
            continue
        if args['type'] and ev['type'] not in args['type']:
            continue

        plotted = plotted + 1

        if args['colorby'] == 'channel':
            color = colors[ev['channel'] % len(colors)]
        elif args['colorby'] == 'event':
            color = colors[ev['event'] % len(colors)]
        elif args['colorby'] == 'file':
            color = colors[i % len(colors)]
        else:  # 'trace'
            color = colors[(total_plotted + plotted) % len(colors)]

        # Apply any options
        if options['shiftx'] is not None:
            ev['times'] += float(options['shiftx'])
        if options['shifty'] is not None:
            ev['responses'] += float(options['shifty'])
        if options['scalex'] is not None:
            np.multiply(ev['times'], float(options['scalex']),
                        out=ev['times'], casting='unsafe')
        if options['scaley'] is not None:
            np.multiply(ev['responses'], float(options['scaley']),
                        out=ev['responses'], casting='unsafe')

        if args['smooth']:
            handle, = smooth.plot(ax, args['smooth'][0], args['smooth'][1],
                                  ev['times'], ev['responses'],
                                  c=color, **plot_kw)
        else:
            handle, = ax.plot(ev['times'], ev['responses'],
                              c=color, **plot_kw)
            handles.append([handle, {'type': ev['type'],
                                     'event': ev['event'],
                                     'channel': ev['channel'],
                                     'file': i}])

    # Make sure axis is not empty
    if plotted == 0:
        print(('Trying to create empty axis for \'{}\', '
              'check your filters.').format(f))
        sys.exit(1)
    total_plotted += plotted

    # Setup ticks
    ax.ticklabel_format(axis='y', style='sci', scilimits=(-1, 3))
    if i != 0 and not args['overlay']:  # Remove all but top exponent
        ax.yaxis.offsetText.set_visible(False)

    # Text / Names
    if not args['overlay'] and args['names'] is not None:
        name_count = len(args['names'])
        if name_count == 0:
            name = data['sample']
        elif i < name_count:
            name = args['names'][i]
        else:
            name = ''
        ax.annotate(name,
                    xy=(1, 1), xycoords='axes fraction',
                    xytext=(-5, -5), textcoords='offset points',
                    fontsize=10, ha='right', va='top')

    # Label the peaks, requires TIC and event per peak
    if args['labelpeaks']:
        plotfuncs.labelpeaks(args['labelpeaks'], axes, data['traces'])

# Add any annotations
if args['annotate']:
    plotfuncs.annotate(args['annotate'])

# Add legend
if args['legend']:
    plotfuncs.legend(args['legend'], handles)

# Hack for pgf not recognising none as labelcolor
plt.xlabel(xlabel)
if args['outfile'] and args['outfile'].endswith('pgf'):
    plotfuncs.set_shared_ylabel(ylabel, axes, fig)
else:
    fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none',
                    top='off', bottom='off', left='off', right='off')
    plt.ylabel(ylabel)

plt.tight_layout()

if args['outfile']:
    plt.savefig(args['outfile'])
if not args['noshow']:
    plt.show()
