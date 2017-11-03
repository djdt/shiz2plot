import numpy as np
import re


name_regex = re.compile('m/z(.)(\d).*?([\d\.]+)>([\d\.]+)')


def parse(filename, fileno=0):
    data = {'sample': None, 'id': None, 'traces': []}
    with open(filename) as fp:
        line = fp.readline()  # Skip header
        line = fp.readline()
        delim = re.match('.*(.)LabSolutions\n', line).group(1)
        while line:
            if line == '[Sample Information]\n':
                # Extract sample info
                while line != '\n':
                    info = line.split(delim)
                    if info[0] == 'Sample Name':
                        data['sample'] = info[1].rstrip()
                    elif info[0] == 'Sample ID':
                        data['id'] = info[1].rstrip()
                    line = fp.readline()
            elif line == '[MS Chromatogram]\n':
                # Extract trace information
                line = fp.readline().rstrip()
                m_type = re.match('m/z.(\d)-(\d)MS\(E(.)\)\s*(.*$)', line)
                event = int(m_type.group(2))
                ion_mode = m_type.group(3)
                # Check if MRM or TIC
                if m_type.group(4) == 'TIC':
                    trace_type = 'tic'
                    precursor, product = None, None
                else:
                    trace_type = 'mrm'
                    m_mrm = re.match('m/z\ ([\d\.]+)>([\d\.]+)',
                                     m_type.group(4))
                    precursor = float(m_mrm.group(1)),
                    product = float(m_mrm.group(2))
                # Skip unwanted
                while not line.startswith('R.Time'):
                    line = fp.readline()
                line = fp.readline()
                # Read data
                times, resps = [], []
                while line != '\n':
                    row = line.split(delim)
                    times.append(row[0])
                    resps.append(row[1])
                    line = fp.readline()

                # Calculate channel
                channel = 0
                for trace in data['traces']:
                    if precursor and precursor == trace['precursor'] and \
                                  trace_type == trace['type']:
                        channel += 1
                data['traces'].append({
                    'file': fileno,
                    'type': trace_type, 'mode': ion_mode,
                    'event': event, 'channel': channel,
                    'precursor': precursor, 'product': product,
                    'times': np.array(times, dtype=float),
                    'responses': np.array(resps, dtype=int)
                    })
            line = fp.readline()
    return data
