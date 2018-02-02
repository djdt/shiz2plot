base16_colors = ['#4271ae', '#f5871f', '#c82829',
                 '#8959a8', '#eab700', '#718c00', '#3e999f']


def get_color(x: int, colors=base16_colors):
    return colors[x % len(colors)]
