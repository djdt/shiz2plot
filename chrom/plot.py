import numpy

from chrom.file import File, Trace
from chrom.options import Options
from chrom.filter import Filter
from chrom.keywords import Keywords

from util.colors import base16_colors


class Plot(object):
    def __init__(self, string: str, default_filter: Filter,
                 default_options: Options,
                 default_poltkws: Keywords):
        """Format for string is <filename>[:<filter>[:<options>[:<plotkw>]]]"""

        self.filter = default_filter
        self.options = default_options
        self.plotkws = default_poltkws

        self.parse(string)

        self.handles = []
        # if colorby not in ['channel', 'event', 'file']:
        #     raise ValueError("Plot: Invalid colorby value " + colorby)

    def parse(self, string: str):
        """Format is <filename>[:<options>[:<filter>]]"""

        tokens = string.split(':')
        if len(tokens) > 4:
            raise TypeError("Plot.parse: To many tokens recieved!")

        self.file = File(tokens[0])

        if len(tokens) > 1:
            self.filter.parse(tokens[1])
        if len(tokens) > 2:
            self.options.parse(tokens[2])
        if len(tokens) > 3:
            self.plotkws.parse(tokens[3])

    def assign_axis(self, axes):
        if hasattr(self.options, 'axis'):
            return axes[self.options.axis[0], self.options.axis[1]]
        else:
            return axes[self.file.fileid, 0]

    def get_color(self, trace: Trace, colors=base16_colors):
        if hasattr(self.file, self.options.colorby):
            # Set color by colorby value
            return colors[
                getattr(self.file, self.options.colorby) % len(colors)]
        elif hasattr(trace, self.options.colorby):
            return colors[
                getattr(trace, self.options.colorby) % len(colors)]
        else:
            print("Options.gen_color: unable to find attr {}".format(
                self.options.colorby))
            return "#000000"

    def label_peaks(self, ax, labels, by='event'):
        for i, label in enumerate(labels):
            xy = (0, 0)
            for trace in self.filter.filter(self.file):
                if getattr(trace, by) == i:
                    peak = trace.detect_peak()
                    if peak[1] > xy[1]:
                        xy = peak
            ax.annotate(label, xy=xy, xytext=(0, 5),
                        xycoords='data', textcoords='offset points',
                        va='bottom', ha='center')

    def shift_and_scale(self, trace: Trace):
            if not hasattr(self, 'scale') and not hasattr(self, 'shift'):
                return trace.times, trace.responses

            # Create a new trace object and copy data into it
            times, responses = trace.times[:], trace.responses[:]
            # Apply shift and scale operations
            if hasattr(self, 'shift'):
                numpy.add(times, self.shift[0], out=times)
                numpy.add(responses, self.shift[1], out=responses)
            if hasattr(self, 'scale'):
                numpy.multiply(times, self.scale[0],
                               out=times)
                numpy.multiply(responses, self.scale[1],
                               out=responses)
            return times, responses

    def plot(self, axes):
        plotkws = self.plotkws.get().copy()
        ax = self.assign_axis(axes)
        # Filter traces and plot them
        for i, trace in enumerate(self.filter.filter(self.file)):
            # Create color for trace if needed
            if not hasattr(self.plotkws, 'color'):
                plotkws['color'] = self.get_color(trace)

            # Plot the traces and store handles
            handle, = ax.plot(*self.shift_and_scale(trace),
                              **plotkws)
            self.handles.append(handle)

        # Add the names
        if hasattr(self.options, 'name'):
            name = self.options.name
        else:
            name = self.file.name
        ax.annotate(name,
                    xy=(1, 1), xycoords='axes fraction',
                    xytext=(-5, -5), textcoords='offset points',
                    fontsize=10, ha='right', va='top')

        # Label peaks
        if hasattr(self.options, 'peaklabels'):
            self.label_peaks(ax, self.options.peaklabels)
