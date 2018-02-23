import yaml
from util.valueparse import convert_string_values


def stringify_dict(d: dict):
    return ",".join(["{}={}".format(k, v) for k, v in d.items()])


def import_cfg(path: str):

    defaults = {'filter': {}, 'options': {}, 'plotkws': {}}
    files = []

    with open(path, 'r') as fp:
        cfg = yaml.load(fp)

        for key, val in cfg.items():
            if key in defaults.keys():
                defaults[key] = {k.lower(): convert_string_values(v)
                                 for k, v in val.items()}
            else:
                file = {'filter': {}, 'options': {}, 'plotkws': {}}
                for fkey in file.keys():
                    try:
                        file[fkey] = val[fkey]
                    except KeyError:
                        pass
                files.append("{}:{}:{}:{}".format(
                    key,
                    stringify_dict(file['filter']),
                    stringify_dict(file['options']),
                    stringify_dict(file['plotkws'])))

    return files, defaults
