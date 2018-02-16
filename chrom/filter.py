from chrom.file import File
from util.kvparser import KeyValParser
from util.valueparse import is_or_in_either


class Filter(KeyValParser):
    VALID_KEYS = {
        "mode": "(str) detection mode. \'tic\' or \'mrm\'.",
        "ion_mode": "(str) ionisation mode. \'+\' or \'-\'.",
        "event": "(int) event id.",
        "channel": "(int) channel id.",
        "precursor": "(float) precursor ion m/z.",
        "product": "(float) product ion m/z.",
        "traceid": "(int) unique trace id.",

        "path": "(str) absolute path to file.",
        "name": "(name) the name of the sample.",
        "id": "(int) the id of the sample.",
        "fileid": "(int) unique file id.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _key_is_valid(self, key):
        return key in Filter.VALID_KEYS.keys()

    def filter(self, file: File):
        key_found = False
        filtered = []
        for key in self.get():
            if hasattr(file, key):  # Check key in file
                if getattr(file, key) in getattr(self, key):
                    return file.traces
                else:
                    return []
            else:
                for trace in file.traces:  # Check key in traces
                    if hasattr(trace, key):
                        if is_or_in_either(getattr(self, key),
                                           getattr(trace, key)):
                            key_found = True
                            filtered.append(trace)
        return filtered if key_found else file.traces
