import re
import os.path
import numpy


class Trace(object):
    TRACE_ID = 0

    def _gen_uid(self):
        id = Trace.TRACE_ID
        Trace.TRACE_ID += 1
        return id

    def __init__(self, mode='tic', ion_mode='+',
                 event=0, channel=0, precursor=0.0, product=0.0,
                 times=numpy.zeros(0, dtype=float),
                 responses=numpy.zeros(0, dtype=int)):
        self.mode = mode
        self.ion_mode = ion_mode
        self.event = event
        self.channel = channel
        self.precursor = precursor
        self.product = product
        self.times = times
        self.responses = responses

        # Gen unique ID
        self.traceid = self._gen_uid()

    def same_channel(self, other):
        return self.precursor > 0.0 and self.precursor == other.precursor

    def detect_peak(self):
        # This method doesn't work with non-symmetric peaks
        # gradient = numpy.gradient(self.responses)
        # peak = int((numpy.argmax(gradient) + numpy.argmin(gradient)) / 2)
        # This method should be faster too
        peak = numpy.argmax(self.responses)

        return self.times[peak], self.responses[peak]


class File(object):
    FILE_ID = 0

    def _gen_uid(self):
        id = File.FILE_ID
        File.FILE_ID += 1
        return id

    def __init__(self, path: str, format='shimadzu'):
        self.format = format
        if not os.path.exists(path):
            raise AttributeError('File {} does not exist!'.format(path))
        self.path = os.path.abspath(path)
        self.name = ""
        self.id = -1
        self.fileid = self._gen_uid()

        self.parse(path)

    def parse(self, path: str):
        if self.format != 'shimadzu':
            raise TypeError('Uknown format {}!'.format(self.format))
        self.name = ""
        self.id = -1
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
                    m_type = re.match('m/z.(\d+)-(\d+)MS\(\w(.)\)\s*(.*$)',
                                      line)
                    if m_type is None:
                        print(line)
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

                    tracedata.times = numpy.array(times, dtype=float)
                    tracedata.responses = numpy.array(resps, dtype=int)

                    # Calculate channel
                    for trace in self.traces:
                        if trace.same_channel(tracedata):
                            tracedata.channel += 1
                    self.traces.append(tracedata)
                line = fp.readline()
