from util.kvparser import KeyValParser


class Options(KeyValParser):
    VALID_KEYS = {
        "axis": "(int, int) position of the plot.",
        "colorby": "(str) attribute used to determine color.",
        "scale": "(float, float) scale the plot data.",
        "shift": "(float, float) shift the plot data.",
        "xlim": "(float, float) define x limits for the data.",
        "ylim": "(float, float) define y limits for the data.",
        "legend": "legend entries for the plot.",
        "name": "(str) name of the plot.",
        "peaklabels": "(list) labels for peaks, from left.",
        "smooth": "(int) smooth data with \'int\' order."
    }
    """Stores per-file options for plotting."""
    def __init__(self, *args, **kwargs):
        """Takes one optional argument, a string passed to .parse."""
        super().__init__(*args, **kwargs)

    def _key_is_valid(self, key):
        return key in Options.VALID_KEYS.keys()
