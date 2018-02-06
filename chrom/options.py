from chrom.kvparser import KeyValParser


class Options(KeyValParser):
    VALID_KEYS = {
        "axis": "(int, int) position of the plot.",
        "colorby": "(string) attribute used to determine color.",
        "scale": "(float, float) scale the plot data.",
        "shift": "(float, float) shift the plot data.",
        "name": "(string) name of the plot.",
        "peaklabels": "(list) labels for peaks, from left.",
        "smooth": "(int) smooth data with \'int\' order."
    }
    """Stores per-file options for plotting."""
    def _key_is_valid(self, key):
        return key in Options.VALID_KEYS.keys()

    def __init__(self, *args, **kwargs):
        """Takes one optional argument, a string passed to .parse."""
        super().__init__(*args, **kwargs)
