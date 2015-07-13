import json

from ckan.plugins.toolkit import missing, _

def shortcode_validate(key, data, errors, context):
    """
    Accept shortcodes in the following forms
    and convert to a json list for storage:

    1. a list of strings, eg.

       ["code-one", "code-two"]

    2. a single string value with semicolon-separated values

       "code-one;code-two"

    """
    # just in case there was an error before our validator,
    # bail out here because our errors won't be useful
    if errors[key]:
        return

    value = data[key]
    if value is missing:
        return json.dumps([])
    if isinstance(value, basestring):
        value = value.split(';')
    if not isinstance(value, list):
        errors[key].append(_('expecting list of strings'))
        return

    out = []
    for element in value:
        if not isinstance(element, basestring):
            errors[key].append(_('invalid type for shortcode: %r')
                % element)
            continue
        if isinstance(element, str):
            try:
                element = element.decode('utf-8')
            except UnicodeDecodeError:
                errors[key]. append(_('invalid encoding for "%s" value')
                    % lang)
                continue
        out.append(element)

    # XXX: future: check values against valid choices for this field
    # using @scheming_validator decorator to get the form field name

    if not errors[key]:
        data[key] = json.dumps(out)


def shortcode_output(value):
    """
    Return stored json representation as a list, if
    value is already a list just pass it through.
    """
    if isinstance(value, list):
        return value
    if value is None:
        return []
    try:
        return json.loads(value)
    except ValueError:
        return [value]

def codeset_create_name(key, data, errors, context):
    codeset_type = None
    codeset_value = None
    i = 0
    while True:
        extra_key = ('extras', i, 'key')
        if extra_key not in data:
            break
        if data[extra_key] == 'codeset_type':
            codeset_type = data[('extras', i, 'value')]
        if data[extra_key] == 'codeset_value':
            codeset_value = data[('extras', i, 'value')]
        i += 1

    if codeset_type and codeset_value:
        data[key] = '-'.join(('codeset', codeset_type, codeset_value))
