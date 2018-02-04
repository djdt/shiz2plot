from cfile import File
from coptions import Options
from cfilter import Filter
from ckeywords import Keywords

from colors import get_color


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
            raise TypeError(
                    "Plot.parse: Format is <filename>"
                    "[:<filter>[:<options>[:<plotkw]]]")

        self.file = File(tokens[0])

        if len(tokens) > 1:
            self.filter.parse(tokens[1])
        if len(tokens) > 2:
            self.options.parse(tokens[2])
        if len(tokens) > 3:
            self.plotkws.parse(tokens[3])

    def plot(self, axes):
        # Determine if color by trace is needed
        gen_color = True
        if hasattr(self.plotkws, 'color'):
            gen_color = False
        elif hasattr(self.file, self.options.colorby):
            gen_color = False
            # Set color by colorby value
            self.plotkws.color = get_color(
                getattr(self.file, self.options.colorby))

        # Filter traces and plot them
        for trace in self.filter.filter(self.file):
            # Create color for trace if needed
            if gen_color and hasattr(trace, self.options.colorby):
                self.plotkws.color = get_color(
                    getattr(trace, self.options.colorby))

            ax = axes[self.options.axis[0], self.options.axis[1]]

            # Plot the traces and store handles
            handle, = ax.plot(trace.times, trace.responses,
                              **self.plotkws.__dict__)
            self.handles.append(handle)

            # Add the names
            ax.annotate(self.file.name,
                        xy=(1, 1), xycoords='axes fraction',
                        xytext=(-5, -5), textcoords='offset points',
                        fontsize=10, ha='right', va='top')
