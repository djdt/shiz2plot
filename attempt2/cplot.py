from cfile import File
from coptions import Options
from cfilter import Filter
from ckeywords import Keywords

from colors import get_color


class Plot(object):
    DEFAULT_OPTIONS = {"axis": None, "colorby": "channel",
                       "scale": (1., 1.), "shift": (0., 0.)}
    DEFAULT_KEYWORDS = {"linewidth": 0.75}

    def __init__(self, string: str, axis=None,
                 scale=(1., 1.), shift=(0., 0.),
                 colorby='channel'):
        """Format for string is <filename>[:<filter>[:<options>[:<plotkw>]]]"""
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
        self.options = Options(**self.DEFAULT_OPTIONS)
        self.keywords = Keywords(**self.DEFAULT_KEYWORDS)

        if len(tokens) > 1:
            self.filter = Filter(tokens[1])
        if len(tokens) > 2:
            self.options.parse(tokens[2])
        if len(tokens) > 3:
            self.keywords.parse(tokens[3])

    def get_traces(self):
        return self.filter.filter(self.file)

    def plot(self, axes):
        # Determine if color by trace is needed
        gen_color = True
        if hasattr(self.keywords, 'color'):
            gen_color = False
        elif hasattr(self.file, self.options.colorby):
            gen_color = False
            # Set color by colorby value
            self.keywords.color = get_color(
                getattr(self.file, self.options.colorby))

        for trace in self.filter.filter(self.file):
            # Create color for trace
            if gen_color and hasattr(trace, self.options.colorby):
                self.keywords.color = get_color(
                    getattr(trace, self.options.colorby))

            handle, = axes[self.options.axis[0], self.options.axis[1]].plot(
                trace.times, trace.responses,
                **self.keywords.__dict__)
            self.handles.append(handle)
