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
from util.config import import_cfg

DEFAULTS = {'filter': {},
            'options': {'colorby': 'channel'},
            'plotkws': {'linewidth': 0.75},
            }


class ListKeysAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):

        if values == 'filter':
            valid = Filter.VALID_KEYS
        elif values == 'options':
            valid = Options.VALID_KEYS
        elif values == 'plotkws':
            valid = {}  # Needs to be implemented

        print("default key/values:")
        print("\t" + "\n\t".join("{} -> {}".format(
              k, v) for k, v in DEFAULTS[values].items()))
        print("valid keys:")
        print("\t" + "\n\t".join("{} -> {}".format(
              k, v) for k, v in valid.items()))

        parser.exit()


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Plots Shimadzu chromatography data.',
        epilog='For filters, options, plotkws see listkeys.')
    # Input / output
    parser.add_argument('infiles', nargs='*',
                        metavar='<file>[:<filter>[:<options>[:<plotkws>]]]',
                        help='Input files and options.')
    parser.add_argument('-c', '--config',
                        help='Import options from a config file,'
                        ' ignores other inputs.')
    parser.add_argument('-o', '--output',
                        help='Output filename and format.')
    parser.add_argument('-S', '--noshow', action='store_true',
                        help='Don\'t show the image.')
    # Options
    parser.add_argument('--scale', nargs=2, type=float,
                        default=(0.9, 0.9), metavar=('X', 'Y'),
                        help='The figure scale.')
    parser.add_argument('-T', '--notex', action='store_true',
                        help='Don\'t use latex parameters.')

    parser.add_argument('--filter', metavar='<key>=<value>,...',
                        help='Filter all files.')
    parser.add_argument('--options', metavar='<key>=<value>,...',
                        help='Options that apply to all files.')
    parser.add_argument('--plotkws', metavar='<key>=<value>,...',
                        help='Key and values to pass to plots.')
    # Text
    parser.add_argument('--xlabel', default='Time (\\si{\\minute})',
                        help='X-axis label.')
    parser.add_argument('--ylabel', default='Response',
                        help='Y-axis label.')

    parser.add_argument('--annotate', nargs='+',
                        metavar='<text>:<key>=<value>,...:axis',
                        help=('Add an annotation to the selected axis. '
                              'Omit \'xytext\' if arrow is not needed.'))
    parser.add_argument('--legend', nargs='+',
                        help='Text for legends.')

    # Help
    parser.add_argument('--listkeys', action=ListKeysAction,
                        choices=['filter', 'options', 'plotkws'],
                        help='List default and available keys.')

    args = parser.parse_args(args)

    # Import the config if it exists
    if args.config is not None:
        cfgfiles, defaults = import_cfg(args.config)
        for key, val in defaults.items():
            DEFAULTS[key].update(val)
        args.infiles.extend(cfgfiles)

    # Parse infiles and update the default options
    if args.infiles is not None:
        infiles = []
        for f in args.infiles:
            try:
                infiles.append(
                    Plot(f, Filter(args.filter, **DEFAULTS['filter']),
                         Options(args.options, **DEFAULTS['options']),
                         Keywords(args.plotkws, **DEFAULTS['plotkws'])))
            except KeyError as e:
                parser.error("Invalid {} key \'{}\'".format(
                    e.args[1].__name__, e.args[0]))
        args.infiles = infiles

    if len(args.infiles) == 0:
        parser.error("No input files detected!")

    return vars(args)


def add_annotations(annotations, axes):
    default_kwargs = {'xycoords': 'axes fraction',
                      'textcoords': 'axes fraction',
                      'va': 'bottom', 'ha': 'center',
                      'arrowprops': dict(arrowstyle='<-', lw=0.75)}

    for an in annotations:
        tokens = an.split(':')
        text = tokens[0]
        kwargs = Keywords(tokens[1], **default_kwargs)
        if not hasattr(kwargs, 'xytext'):
            kwargs.xytext = kwargs.xy
            kwargs.arrowprops = None

        if len(tokens) > 2:
            ax = tokens[2].strip('[]()').split(',')
            ax = [int(x) for x in ax]
            axes[ax[0], ax[1]].annotate(text, **kwargs.get())
        else:
            plt.annotate(text, **kwargs.get())


def add_legends(legends):
    lines = []
    for i, label in enumerate(legends):
        line = mlines.Line2D([], [],
                             color=base16_colors[i % len(base16_colors)],
                             linewidth=0.75, label=label)
        lines.append(line)
    plt.legend(handles=lines, framealpha=1.0, fancybox=False)


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
        add_annotations(args['annotate'], axes)

    # Add legends
    if args['legend'] is not None:
        add_legends(args['legend'])

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
