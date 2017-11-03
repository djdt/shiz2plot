import numpy as np


def parse(filename, fileno):
    data = {'sample': None, 'id': None, 'traces': []}
    event = 0
    with open(filename) as fp:
        delim = ','
        line = fp.readline()
        while line:
            row = line.rstrip().split(delim)
            if row[0] == 'name':
                data['sample'] = row[1]
            elif row[0] == 'id':
                data['id'] = row[1]
            elif row[0] == 'precursor':
                channel = 0
                precursor = row[1]
                line = fp.readline()
                row = line.rstrip().split(delim)
                product = row[1]
                for d in data['traces']:
                    if d['precursor'] == precursor:
                        channel += 1
                line = fp.readline()
                ts, rs = [], []
                while line:
                    row = line.rstrip().split(delim)
                    if row[0] == '':
                        break
                    ts.append(row[0])
                    rs.append(row[1])
                    line = fp.readline()

                data['traces'].append({
                    'file': fileno,
                    'event': event, 'channel': channel,
                    'precursor': precursor, 'product': product,
                    'times': np.array(ts, dtype=float),
                    'responses': np.array(rs, dtype=int)
                    })
                event += 1
            line = fp.readline()
    return data
