import numpy as np


def detect_peaks(ax, data, min_height, events=None, channels=None):

    for trace in data['traces']:
        # if events and ev['event'] not in events:
        #     continue
        # if channels and ev['channel'] not in channels:
        #     continue
        # Find start, end
        starts, ends = [], []
        last = trace['responses'][0]
        for i, y in enumerate(trace['responses']):
            if y > min_height and last < min_height:
                starts.append(i)
            if y < min_height and last > min_height:
                ends.append(i)
        if len(starts) != len(ends):
            print('start and ends diff length')

        peak_inds = []
        for pos in zip(starts, ends):
            peak = np.argmax(np.array(trace['responses'][pos[0], pos[1]]))
            peak_inds.append(peak)
        # Interpolate plot
        # p90 = np.percentile(ev['responses'], 95)
        # inds = np.where(ev['responses'] > p90)
        # rtime = np.mean(ev['times'][inds])

        ax.scatter(trace['times'][peak_inds],
                   trace['responses'][peak_inds], marker='v')
        # ax.text(rtime, ev['responses'].max(),
        #              '{rtime:.3f}'.format(rtime=rtime),
        #              ha='center', va='bottom')
