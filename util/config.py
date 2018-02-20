import configparser
from util.valueparse import convert_string_values


def import_chrom_config(conf_file: str):
    cfg = configparser.ConfigParser()
    cfg.read(conf_file)

    defaults = {'filter': {}, 'options': {}, 'plotkws': {}}

    if 'FILTER' in cfg:
        for k, v in cfg['FILTER'].items():
            defaults['filter'][k] = convert_string_values(v)
    if 'OPTIONS' in cfg:
        for k, v in cfg['OPTIONS'].items():
            defaults['options'][k] = convert_string_values(v)
    if 'PLOTKWS' in cfg:
        for k, v in cfg['PLOTKWS'].items():
            defaults['plotkws'][k] = convert_string_values(v)

    return defaults
