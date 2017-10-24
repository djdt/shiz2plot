def set_shared_ylabel(ylabel, axes, figure):

    axes[0].set_ylabel(ylabel)
    for ax in axes[1:]:
        ax.set_ylabel('')
    # Calculate center of plots
    top = axes[0].get_position().y1
    bot = axes[-1].get_position().y0
    ypos = (bot + top) / 2.0

    # Calculate the x pos after transform
    # pos = axes[0].yaxis.label.get_position()
    # xpos = figure.transFigure.inverted().transform(pos)[0]
    xpos = axes[0].get_position().x0 / 2.0

    axes[0].yaxis.set_label_coords(xpos, ypos, transform=figure.transFigure)
