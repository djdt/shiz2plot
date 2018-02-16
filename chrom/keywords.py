from util.kvparser import KeyValParser


class Keywords(KeyValParser):
    """Stores per-file options for plotting."""

    def __init__(self, *args, **kwargs):
        """Takes one optional argument, a string passed to .parse."""
        super().__init__(*args, **kwargs)
