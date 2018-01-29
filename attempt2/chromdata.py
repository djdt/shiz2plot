import numpy as np


class ChromFilter(object):
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], str):



class TraceData(object):
    def __init__(self, mode='tic', ion_mode='positive',
                 event=0, channel=0, precursor=0.0, product=0.0,
                 data=np.zeros((2, 0), dtype=float)):
        self.mode = mode
        self.ion_mode = ion_mode
        self.event = event, self.channel = channel
        self.precursor = precursor, self.product = product
        self.data = data

    def mode_as_int(self):
        if self.mode == 'tic':
            return 0
        else:
            return 1


class ChromData(object):
    def __init__(self, file_path, name, id, traces=[], format='shimadzu'):
        self.file_path = file_path
        self.name = name
        self.format = format
        self.id = id
        self.traces = traces

    def add_trace(self, trace_data: TraceData):
        self.traces.append(trace_data)

    def filter_traces(self, filter):

