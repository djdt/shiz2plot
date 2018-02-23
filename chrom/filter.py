from chrom.file import File, Trace
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

    def _check_key(self, key, obj):
        if hasattr(obj, key) and is_or_in_either(getattr(self, key),
                                                 getattr(obj, key)):
            return True
        return False

    def _filter_trace(self, trace: Trace):
        for key in self.get():
            if hasattr(trace, key):
                if not is_or_in_either(getattr(self, key),
                                       getattr(trace, key)):
                    return False
        return True

    def filter(self, file: File):
        for key in self.get():
            if hasattr(file, key):
                if not is_or_in_either(getattr(self, key),
                                       getattr(file, key)):
                    return []

        return [t for t in file.traces if self._filter_trace(t)]
