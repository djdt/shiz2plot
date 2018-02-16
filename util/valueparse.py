def parse_value(value: str):
    try:
        if '.' in value:
            return float(value)
        else:
            return int(value)
    except ValueError:
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        else:
            return value


def convert_string_values(values: str):
    opening = values[0]
    values = values.strip('[]()').split(',')
    values = [parse_value(x) for x in values]

    if len(values) == 1:
        return values[0]
    elif opening == '(':
        return tuple(values)
    else:
        return values
