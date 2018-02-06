COLOR_DICT = {
    'base16': ['#4271ae', '#f5871f', '#c82829', '#8959a8',
               '#eab700', '#718c00', '#3e999f'],
}

COLOR_ORDER = {'blue': 0, 'orange': 1, 'red': 2, 'purple': 3,
               'yellow': 4, 'green': 5, 'cyan': 6}


def get_colors(scheme, color_order=None):
    if color_order is None:
        return COLOR_DICT[scheme]
    colors = []
    for color in color_order:
        colors.append(COLOR_DICT[scheme][COLOR_ORDER[color]])
    return colors
