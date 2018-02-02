import re
import numpy


class Trace(object):
    def __init__(self, mode='tic', ion_mode='+',
                 event=0, channel=0, precursor=0.0, product=0.0,
                 data=numpy.zeros((2, 0), dtype=float)):
        self.mode = mode
        self.ion_mode = ion_mode
        self.event = event
        self.channel = channel
        self.precursor = precursor
        self.product = product
        self.data = data

    def same_channel(self, other):
        return self.precursor == other.precursor


class File(object):
    def __init__(self, path: str, format='shimadzu'):
        self.format = format
        self.parse(path)

    def parse(self, path: str):
        if self.format != 'shimadzu':
            raise TypeError('Uknown format ' + self.format)
        self.path = path
        self.traces = []

        with open(self.path) as fp:
            line = fp.readline()  # Skip header
            line = fp.readline()
            delim = re.match('.*(.)LabSolutions\n', line).group(1)
            while line:
                if line == '[Sample Information]\n':
                    # Extract sample info
                    while line != '\n':
                        info = line.split(delim)
                        if info[0] == 'Sample Name':
                            self.name = info[1].rstrip()
                        elif info[0] == 'Sample ID':
                            self.id = info[1].rstrip()
                        line = fp.readline()
                elif line == '[MS Chromatogram]\n':
                    # Extract trace information
                    tracedata = Trace()
                    line = fp.readline().rstrip()
                    m_type = re.match('m/z.(\d)-(\d)MS\(E(.)\)\s*(.*$)', line)
                    tracedata.event = int(m_type.group(2))
                    tracedata.ion_mode = m_type.group(3)
                    # Check if MRM or TIC
                    if m_type.group(4) != 'TIC':
                        tracedata.mode = 'mrm'
                        m_mrm = re.match('m/z\ ([\d\.]+)>([\d\.]+)',
                                         m_type.group(4))
                        tracedata.precursor = float(m_mrm.group(1))
                        tracedata.product = float(m_mrm.group(2))
                    # Skip unwanted
                    while not line.startswith('R.Time'):
                        line = fp.readline()
                    line = fp.readline()
                    # Read data
                    times, resps = [], []
                    while line != '\n':
                        row = line.split(delim)
                        times.append(row[0])
                        resps.append(row[1])
                        line = fp.readline()

                    tracedata.data = numpy.column_stack((
                        numpy.array(times, dtype=float),
                        numpy.array(resps, dtype=float)))

                    # Calculate channel
                    for trace in self.traces:
                        if trace.same_channel(tracedata):
                            tracedata.channel += 1
                    self.traces.append(tracedata)
                line = fp.readline()


class Options(object):
    """Stores per-file options for plotting.
    """
    def __init__(self, *args, **kwargs):
        """Takes one optional argument, a string to parse."""
        if len(args) > 1:
            raise TypeError(
                "File: Takes 0 or 1 argument, {} given.".format(len(args)))
        elif len(args) == 1:
            self.parse(args[0])
        for key, val in kwargs.items():
            setattr(self, key, val)

    def _convert_value(self, value: str):
        try:
            if '.' in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            pass
        return value

    def parse(self, string: str):
        """Format of string is a comma separated list of <key>=<val>self.
        Values may be a list."""
        if len(string) == 0:
            return

        string = string.strip().lower()
        tokens = re.split('\,(?=\w+\=)', string)

        for token in tokens:
            key, vals = token.split('=')

            vals = vals.strip('[]()').split(',')
            vals = [self._convert_value(x) for x in vals]

            setattr(self, key, vals)

    def add_non_existing(self, *args, **kwargs):
        """Only adds new attributes, will not overwrite existing."""
        for key, val in kwargs.items():
            setattr(self, key, val)


class Filter(Options):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def filter(self, chromdata: File):
        filtered = []
        for key in self.__dict__:
            if hasattr(chromdata, key):
                if getattr(chromdata, key) not in getattr(self, key):
                    return None
            else:
                for trace in chromdata.traces:
                    if hasattr(trace, key) and \
                       getattr(trace, key) in getattr(self, key):
                        filtered.append(trace)
        return filtered


class Plot(object):
    def __init__(self, string: str, axis=0):
        """Format for string is <filename>[:<options>[:<filter>]]"""
        self.parse(string)
        self.axis = axis

    def parse(self, string: str):
        """Format is <filename>[:<options>[:<filter>]]"""

        tokens = string.split(':')
        if len(tokens) > 3:
            raise TypeError(
                "Plot.parse: Format is <filename>[:<options>[:<filter>]]")

        self.file = File(tokens[0])
        if len(tokens) > 1:
            self.options = Options(tokens[1])
        if len(tokens) > 2:
            self.filter = Filter(tokens[2])

    def get_traces(self):
        return self.filter.filter(self.file)
