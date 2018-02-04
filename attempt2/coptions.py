from kvparser import KeyValParser


class Options(KeyValParser):
    MAX_AXIS = [0, 0]

    """Stores per-file options for plotting."""

    def _calc_axis(self):
        if self.axis is None:
            self.axis = self.MAX_AXIS[:]
            self.MAX_AXIS[0] += 1
        else:
            if self.axis[0] > self.MAX_AXIS[0]:
                self.MAX_AXIS[0] = self.axis[0]
            if self.axis[1] > self.MAX_AXIS[1]:
                self.MAX_AXIS[1] = self.axis[1]

    def __init__(self, *args, **kwargs):
        """Takes one optional argument, a string passed to .parse."""
        super().__init__(*args, **kwargs)
        self._calc_axis()
