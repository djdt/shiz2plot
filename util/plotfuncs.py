import matplotlib.pyplot as plt
import numpy as np


def labelpeaks(labeldata, file_no, axes, traces):
    for label, filter in labeldata:
        xy = [0, 0]
        if filter['file'] and file_no not in filter['file']:
            continue
        for trace in traces:
            if filter['type'] and trace['type'] not in filter['type']:
                continue
            if filter['channel'] and \
               trace['channel'] not in filter['channel']:
                continue
            if filter['event'] and trace['event'] not in filter['event']:
                continue

            max_index = np.argmax(trace['responses'])
            rtime = trace['times'][max_index]
            height = trace['responses'][max_index]

            # Get the max height of all traces
            if height > xy[1]:
                xy = (rtime, height)
        # Annotate 5pt above the peak
        if xy != [0, 0]:
            axes[file_no].annotate(
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
        for handle, handle_filter in axhandles:
            if handle_filter['type'] not in filter['type']:
                continue
            if handle_filter['event'] not in filter['event']:
                continue
            if handle_filter['channel'] not in filter['channel']:
                continue
            if handle_filter['file'] not in filter['file']:
                continue
            handles.append(handle[0])
            labels.append(text)

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
