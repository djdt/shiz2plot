#!/usr/bin/env python3

import argparse
import sys

import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import matplotlib.lines as mlines

from chrom.plot import Plot
from chrom.filter import Filter
from chrom.options import Options
from chrom.keywords import Keywords

import util.latex as latex
from util.colors import base16_colors

DEFAULT_FILTER = {}
DEFAULT_OPTIONS = {"colorby": "channel"}
DEFAULT_PLOTKWS = {"linewidth": 0.75}


class ListKeysAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if values == 'filter':
            defaults = DEFAULT_FILTER
            valid = Filter.VALID_KEYS
        elif values == 'options':
            defaults = DEFAULT_OPTIONS
            valid = Options.VALID_KEYS
        elif values == 'plotkws':
            defaults = DEFAULT_PLOTKWS
            valid = {}  # Needs to be implemented

        print("default key/values:")
        print("\t" + "\n\t".join("{} -> {}".format(
              k, v) for k, v in defaults.items()))
        print("valid keys:")
        print("\t" + "\n\t".join("{} -> {}".format(
              k, v) for k, v in valid.items()))

        parser.exit()


def parse_args(args):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Plots Shimadzu chromatography data.',
        epilog='For filters, options, plotkws see listkeys.')
    # Input / output
    parser.add_argument('infiles', nargs='+',
                        metavar='<file>[:<filter>[:<options>[:<plotkws>]]]',
                        help='Input files and options.')
    parser.add_argument('-o', '--output',
                        help='Output filename and format.')
    parser.add_argument('-S', '--noshow', action='store_true',
                        help='Don\'t show the image.')
    # Options
    parser.add_argument('--scale', type=float, nargs=2,
                        default=(0.9, 0.9),
                        help='The X and Y scale of the image.')
    parser.add_argument('-T', '--notex', action='store_true',
                        help='Don\'t use latex parameters.')

    parser.add_argument('--filter', type=str,
                        metavar='<key>=<value>[,...]',
                        help='Filter all files.')
    parser.add_argument('--options', type=str,
                        metavar='<key>=<value>[,...]',
                        help='Options that apply to all files.')
    parser.add_argument('--plotkws', type=str,
                        metavar='<key>=<value>[,...]',
                        help='Key and values to pass to plots.')
    # Text
    parser.add_argument('--xlabel', type=str, default='Time (\\si{\\minute})',
                        help='X-axis label.')
    parser.add_argument('--ylabel', type=str, default='Response',
                        help='Y-axis label.')

    parser.add_argument('--annotate', nargs='+',
                        metavar='<text>:<key>=<value>[,...][:<axis>]',
                        help=('Add an annotation to the selected axis, '
                              'omit \'xytext\' if arrow is not needed'))

    # Help
    parser.add_argument('--listkeys',
                        choices=['filter', 'options', 'plotkws'],
                        action=ListKeysAction,
                        help='List default and available keys.')
    parser.add_argument('--legend', nargs='*', type=str,
                        help='Text for legends.')

    args = parser.parse_args(args)

    if args.listkeys is not None:
        return

    # Update the default options

    if args.infiles is not None:
        infiles = []
        for f in args.infiles:
            try:
                infiles.append(
                    Plot(f, Filter(args.filter),
                         Options(args.options, **DEFAULT_OPTIONS),
                         Keywords(args.plotkws, **DEFAULT_PLOTKWS)))
            except KeyError as e:
                parser.error("Invalid {} key \'{}\'".format(
                    e.args[1].__name__, e.args[0]))
        args.infiles = infiles

    return vars(args)


def add_annotation(axes, string: str, annotation=True):
    default_kwargs = {'xycoords': 'axes fraction',
                      'textcoords': 'axes fraction',
                      'va': 'bottom', 'ha': 'center',
                      'arrowprops': dict(arrowstyle='<-', lw=0.75)}
    ax = None

    tokens = string.split(':')
    text = tokens[0]
    kwargs = Keywords(tokens[1], **default_kwargs)
    if len(tokens) > 2:
        ax = tokens[2].strip('[]()').split(',')
        ax = [int(x) for x in ax]

    if not hasattr(kwargs, 'xytext'):
        kwargs.xytext = kwargs.xy
        kwargs.arrowprops = None

    if ax is not None:
        axes[ax[0], ax[1]].annotate(text, **kwargs.get())
    else:
        plt.annotate(text, **kwargs.get())


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

    # Add annotations
    if args['annotate'] is not None:
        for an in args['annotate']:
            add_annotation(axes, an)

    # Add legends
    if args['legend'] is not None:
        lines = []
        for i, label in enumerate(args['legend']):
            line = mlines.Line2D([], [],
                                 color=base16_colors[i % len(base16_colors)],
                                 linewidth=0.75, label=label)
            lines.append(line)
        plt.legend(handles=lines, framealpha=1.0, fancybox=False)

    # Hack for pgf not recognising none as labelcolor
    plt.xlabel(args['xlabel'])
    if args['output'] and args['output'].endswith('pgf'):
        set_shared_ylabel(args['ylabel'], axes, fig)
    else:
        fig.add_subplot(111, frameon=False)
        plt.tick_params(labelcolor='none',
                        top='off', bottom='off', left='off', right='off')
        plt.ylabel(args['ylabel'])

    # Remove uneeded withspace
    plt.tight_layout()

    # Save and/or show the output
    if args['output']:
        plt.savefig(args['output'])
    if not args['noshow']:
        plt.show()
    return


if __name__ == "__main__":
    main(sys.argv[1:])
