import matplotlib.pyplot as plt
import numpy as np

import filters


def labelpeaks(labeldata, axes, traces):
    for label, filter in labeldata:
        fileno = 0
        xy = [0, 0]
        for trace in traces:
            if filters.filter_item(filter, trace):
                max_index = np.argmax(trace['responses'])
                rtime = trace['times'][max_index]
                height = trace['responses'][max_index]

            # Get the max height of all traces
            if height > xy[1]:
                xy = (rtime, height)
                fileno = trace['file']
        # Annotate 5pt above the peak
        if xy != [0, 0]:
            axes[fileno].annotate(
                    label, xy=xy, xytext=(0, 5),
                    xycoords='data', textcoords='offset points',
                    va='bottom', ha='center')


def annotate(annotations):
    for arg in annotations:
        text = arg[0]
        xytext = float(arg[1]), float(arg[2])
        if len(arg) < 5:
            plt.annotate(text, xy=xytext, xytext=xytext,
                         xycoords='axes fraction',
                         textcoords='axes fraction',
                         va='bottom', ha='center')
        else:
            arrow = arg[3]
            xy = float(arg[4]), float(arg[5])
            plt.annotate(text, xy=xy, xytext=xytext,
                         xycoords='axes fraction',
                         textcoords='axes fraction',
                         va='bottom', ha='center',
                         arrowprops=dict(arrowstyle=arrow, lw=0.75))


def legend(legends, axhandles):
    handles, labels = [], []
    for text, filter in legends:
        for handle, h_filter in axhandles:
            if filters.filter_item(filter, h_filter):
                handles.append(handle)
                labels.append(text)
                break

    plt.legend(handles=handles, labels=labels,
               framealpha=1.0, fancybox=False)


def set_shared_ylabel(ylabel, axes, figure):
    axes[0].set_ylabel(ylabel)
    for ax in axes[1:]:
        ax.set_ylabel('')
    # Calculate center of plots
    top = axes[0].get_position().y1
    bot = axes[-1].get_position().y0
    ypos = (bot + top) / 2.0

    # Calculate the x pos after transform
    xpos = axes[0].get_position().x0 / 2.0

    axes[0].yaxis.set_label_coords(xpos, ypos, transform=figure.transFigure)
