import re


FILTER_DICT = {'file': 'f',
               'type': 't',
               'event': 'e',
               'channel': 'c',
               'precursor': 'p',
               'product': 'd'}
TYPE_DICT = {0: 'mrm', 1: 'tic'}


def parse(fstring):
    filter = {'file': [], 'type': [],
              'event': [], 'channel': [],
              'precursor': [], 'product': []}
    for key in filter.keys():
        m = re.search('({short}|{long})([\d\,]+)'.format(
            short=FILTER_DICT[key], long=key), fstring)
        if m is not None:
            filter[key].extend([int(x) for x in m.group(2).split(',')])
    return filter


def parse_args_list(args):
    filter_args = []
    for arg in args:
        tokens = re.split(':', arg)
        filter = parse(tokens[1])
        filter_args.append([tokens[0], filter])
    return filter_args


def filter_item(filter, item):
    for key, val in filter.items():
        if item[key] not in val:
            return False
    return True
