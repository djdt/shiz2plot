from chrom.file import File
from chrom.kvparser import KeyValParser


class Filter(KeyValParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def filter(self, file: File):
        key_found = False
        filtered = []
        for key in self.__dict__:
            if hasattr(file, key):  # Check key in file
                if getattr(file, key) in getattr(self, key):
                    return file.traces
                else:
                    return []
            else:
                for trace in file.traces:  # Check key in traces
                    if hasattr(trace, key) and \
                       getattr(trace, key) in getattr(self, key):
                        key_found = True
                        filtered.append(trace)
        return filtered if key_found else file.traces
