import re


TYPE_DICT = {0: 'mrm', 1: 'tic'}


def parse(args):
    filter_args = []
    for arg in args:
        filter = {'file': [], 'type': [],
                  'event': [], 'channel': [],
                  'precursor': [], 'product': []}
        tokens = re.split(':', arg)
        if len(tokens) != 2:
            raise Exception('Invalid annotation format for filter ' + arg)

        for key in filter.keys():
            m = re.search('(' + key[0] + '|' + key + ')([\d\,]+)',
                          tokens[1])
            if m is not None:
                if key is 'type':
                    filter[key] = [
                            TYPE_DICT[int(x)] for x in m.group(2).split(',')]
                else:
                    filter[key] = [int(x) for x in m.group(2).split(',')]

        filter_args.append([tokens[0], filter])
    return filter_args


def filter_item(filter, item):
    for key, val in filter.items():
        if item[key] not in val:
            return False
    return True
