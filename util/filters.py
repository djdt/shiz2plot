import re


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
                filter[key] = [int(x) for x in m.group(2).split(',')]

        filter_args.append([tokens[0], filter])
    return filter_args


def filter_item(filter, item):
    if filter['file'] and item['file'] not in filter['file']:
        return False
    if filter['type'] and item['type'] == 'tic' and 1 in filter['type']:
        return False
    if filter['type'] and item['type'] == 'mrm' and 0 in filter['type']:
        return False
    if filter['channel'] and item['channel'] not in filter['channel']:
        return False
    if filter['event'] and item['event'] not in filter['event']:
        return False
    if filter['precursor'] and item['precursor'] not in filter['precursor']:
        return False
    if filter['product'] and item['product'] not in filter['product']:
        return False
    return True
