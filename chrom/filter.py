from chrom.file import File, Trace
from util.kvparser import KeyValParser
from util.valueparse import is_or_in_either


class Filter(KeyValParser):
    VALID_KEYS = {
        "mode": "(str) detection mode. \'tic\' or \'mrm\'.",
        "ion_mode": "(str) ionisation mode. \'+\' or \'-\'.",
        "event": "(int,str) event id or name.",
        "channel": "(int) channel id.",
        "precursor": "(float) precursor ion m/z.",
        "product": "(float) product ion m/z.",
        "traceid": "(int) unique trace id.",

        "path": "(str) absolute path to file.",
        "name": "(name) the name of the sample.",
        "id": "(int) the id of the sample.",
        "fileid": "(int) unique file id.",
    }
    LOOKUP = {
        "event": {
            "PFBA": 1, "MPFBA": 2,
            "PFPeA": 3, "M5PFPeA": 4,
            "PFBS": 5, "M3PFBS": 6,
            "PFHxA": 7, "M5PFHxA": 8,
            "PFPeS": 9,
            "PFHpA": 10, "M4PFHpA": 11,
            "PFHxS": 12, "M3PFHxS": 13,
            "PFOA": 14, "M8PFOA": 15,
            "PFHpS": 16,
            "PFNA": 17, "M9PFNA": 18,
            "PFOS": 19, "M8PFOS": 20,
            "PFDA": 21, "M6PFDA": 22,
            "PFNS": 23,
            "PFUnA": 24, "M7PFUnA": 25,
            "PFDS": 26,
            "PFDoA": 27, "MPFDoA": 28,
            "PFTrDA": 29,
            "PFDoS": 30,
            "PFTeDA": 31, "M2PFTeDA": 32,
            "PFHxDA": 33,
            "PFODA": 34
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _key_is_valid(self, key):
        return key in Filter.VALID_KEYS.keys()

    # def _lookup_key(self, key, vals):
    #     if key in Filter.LOOKUP.keys():
    #         print(key)
    #         new_vals = []
    #         for v in [vals]:
    #             new_vals.append(getattr(Filter.LOOKUP[key], v, v))
    #         vals = new_vals
    #     print(vals)
    #     return vals

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
