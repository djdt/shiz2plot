import re


class KeyValParser(object):
    """Parses string of comma separated <key>=<value> pairs."""
    def __init__(self, *args, **kwargs):
        """args -> Optional string that is passed to .parse.
        kwargs -> Stored as sttributes."""

        if len(args) > 1:
            raise TypeError(
                "File: Takes 0 or 1 argument, {} given.".format(len(args)))
        elif len(args) == 1:
            self.parse(args[0])

        for key, val in kwargs.items():
            setattr(self, key, val)

    def _convert_value(self, value: str):
        try:
            if '.' in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            pass
        return value

    def parse(self, string: str, overwrite=True):
        """Parse a string and add values.
            string -> (string) comma separated list of <key>=<val>.
            overwrite -> (bool) overwrite existing attributes."""
        if len(string) == 0:
            return

        string = string.strip().lower()
        tokens = re.split('\,(?=\w+\=)', string)

        for token in tokens:
            key, vals = token.split('=')

            vals = vals.strip('[]()').split(',')
            vals = [self._convert_value(x) for x in vals]
            if len(vals) == 1:
                vals = vals[0]

            if overwrite or not hasattr(self, key):
                setattr(self, key, vals)
