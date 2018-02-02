from cfile import File
from coptions import Options
from cfilter import Filter

from colors import get_color


class Plot(object):
    DEFAULT_OPTIONS = {"linewidth": 0.75}
    MAX_AXIS = [0, 0]

    def _calc_axis(self, axis):
        if axis is None:
            self.axis = self.MAX_AXIS[:]
            self.MAX_AXIS[0] += 1
        else:
            self.axis = axis
            if self.axis[0] > self.MAX_AXIS[0]:
                self.MAX_AXIS[0] = self.axis[0]
            if self.axis[1] > self.MAX_AXIS[1]:
                self.MAX_AXIS[1] = self.axis[1]

    def __init__(self, string: str, axis=None,
                 scale=(1., 1.), shift=(0., 0.),
                 colorby='channel'):
        """Format for string is <filename>[:<options>[:<filter>]]"""
        self.parse(string)
        self._calc_axis(axis)
        self.scale = scale
        self.shift = shift

        self.handles = []
        # if colorby not in ['channel', 'event', 'file']:
        #     raise ValueError("Plot: Invalid colorby value " + colorby)
        self.colorby = colorby

    def parse(self, string: str):
        """Format is <filename>[:<options>[:<filter>]]"""

        tokens = string.split(':')
        if len(tokens) > 3:
            raise TypeError(
                "Plot.parse: Format is <filename>[:<options>[:<filter>]]")

        self.file = File(tokens[0])
        if len(tokens) > 1:
            self.options = Options(tokens[1], **self.DEFAULT_OPTIONS)
        if len(tokens) > 2:
            self.filter = Filter(tokens[2])

    def get_traces(self):
        return self.filter.filter(self.file)

    def plot(self, axes):
        # Determine if color by trace is needed
        gen_color = True
        if hasattr(self.options, 'color'):
            gen_color = False
        elif hasattr(self.file, self.colorby):
            gen_color = False
            # Set color by colorby value
            self.options.color = get_color(getattr(self.file, self.colorby))

        for trace in self.filter.filter(self.file):
            # Create color for trace
            if gen_color and hasattr(trace, self.colorby):
                self.options.color = get_color(getattr(trace, self.colorby))

            handle, = axes[self.axis[0], self.axis[1]].plot(
                trace.times, trace.responses,
                **self.options.__dict__)
            self.handles.append(handle)
