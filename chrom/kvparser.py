import re


class KeyValParser(object):
    """Parses string of comma separated <key>=<value> pairs."""
    def __init__(self, *args, **kwargs):
        """args -> Optional string that is passed to .parse.
        kwargs -> Stored as sttributes."""

        if len(args) > 1:
            raise TypeError(
                "File: Takes 0 or 1 argument, {} given.".format(len(args)))
        elif len(args) == 1 and args[0] is not None:
            self.parse(args[0])

        # Parsed values have priority
        self.update(kwargs, overwrite=False)

    def _convert_value(self, value: str):
        try:
            if '.' in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            pass
        return value

    def _key_is_valid(self, key):
        return True

    def parse(self, string: str, overwrite=True):
        """Parse a string and add values.
            string -> (string) comma separated list of <key>=<val>.
            overwrite -> (bool) overwrite existing attributes."""
        if len(string) == 0:
            return

        string = string.strip()
        tokens = re.split('\,(?=\w+\=)', string)

        for token in tokens:
            key, vals = token.split('=')
            key = key.lower()
            if not self._key_is_valid(key):
                raise KeyError(key, self.__class__)

            vals = vals.strip('[]()').split(',')
            vals = [self._convert_value(x) for x in vals]
            if len(vals) == 1:
                vals = vals[0]

            if overwrite or not hasattr(self, key):
                setattr(self, key, vals)

    def update(self, kwargs: dict, overwrite=False):
        """Adds keys, values to the class.
            kwargs -> (dict) key values to add.
            overwrite -> (bool) overwrite existing."""
        for key, val in kwargs.items():
            if not self._key_is_valid(key):
                raise KeyError(key, self.__class__)
            if overwrite or not hasattr(self, key):
                setattr(self, key, val)

    def get(self):
        return self.__dict__
