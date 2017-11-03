import numpy as np
import re


split_re = re.compile(''',(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''')


def parse(filename, fileno):
    data = {'sample': None, 'id': None, 'traces': []}
    event = 0
    with open(filename) as fp:
        line = fp.readline()
        delim = re.search('File Path(.)', line).group(1)
        while line:
            if line.startswith('Injection Information:'):
                # Extract sample info
                while not line.startswith(','):
                    info = line.split(delim)
                    if info[0] == 'Injection':
                        data['sample'] = info[1].rstrip()
                    elif info[0] == 'Injection Number':
                        data['id'] = info[1].rstrip()
                    line = fp.readline()
            elif line.startswith('Chromatogram Data:'):
                precursor, product = 0.0, 0.0
                # Skip unwanted
                while not line.startswith('Time (min)'):
                    line = fp.readline()
                line = fp.readline()
                # Read data
                times, resps = [], []
                while line and not line.startswith(','):
                    row = re.split(
                        '''{delim}(?=(?:[^'"]|'[^']*'|"[^"]*")*$)'''.format(
                           delim=delim), line)
                    # row = line.split(delim)
                    times.append(row[0])
                    resp = re.sub('[,"]', '', row[2].rstrip())
                    resp = re.sub('\.\d+$', '', resp)
                    resps.append(resp)
                    line = fp.readline()

                # Calculate channel
                channel = 0
                for trace in data['traces']:
                    if precursor == trace['precursor']:
                        channel += 1
                data['traces'].append({
                    'file': fileno,
                    'type': 'tic', 'mode': '-',
                    'event': event, 'channel': channel,
                    'precursor': precursor, 'product': product,
                    'times': np.array(times, dtype=float),
                    'responses': np.array(resps, dtype=int)
                    })
                event += 1
            line = fp.readline()
    return data
