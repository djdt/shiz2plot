from cfile import File
from coptions import Options


class Filter(Options):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def filter(self, file: File):
        filtered = []
        for key in self.__dict__:
            if hasattr(file, key):
                if getattr(file, key) not in getattr(self, key):
                    break
            else:
                for trace in file.traces:
                    if hasattr(trace, key) and \
                       getattr(trace, key) in getattr(self, key):
                        filtered.append(trace)
        return filtered
