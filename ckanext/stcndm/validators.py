import json

from ckan.plugins.toolkit import missing, _
from ckanext.stcndm import helpers as h


def scheming_validator(fn):
    """
    Decorate a validator that needs to have the scheming fields
    passed with this function. When generating navl validator lists
    the function decorated will be called passing the field
    and complete schema to produce the actual validator for each field.
    """
    fn.is_a_scheming_validator = True
    return fn


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
        data[key] = json.dumps([])
        return
    if isinstance(value, basestring):
        value = value.split(';')
    if not isinstance(value, list):
        errors[key].append(_('expecting list of strings'))
        return

    out = []
    for element in value:
        if not isinstance(element, basestring):
            errors[key].append(_('invalid type for shortcode: %r') % element)
            continue
        if isinstance(element, str):
            try:
                element = element.decode('utf-8')
            except UnicodeDecodeError:
                errors[key]. append(_('invalid encoding for "%s" value') % lang)
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


def _data_lookup(key, data):
    value = None
    if key in data:
        value = data[key]
    else:
        i = 0
        while True:
            extra_key = ('extras', i, 'key')
            if extra_key not in data:
                break
            if data[extra_key] == key:
                value = data[('extras', i, 'value')]
            i += 1
    return value


def codeset_create_name(key, data, errors, context):
    codeset_type = _data_lookup(('codeset_type',), data)
    codeset_value = _data_lookup(('codeset_value',), data)
    if codeset_type and codeset_value:
        data[key] = u'codeset-{0}-{1}'.format(codeset_type, codeset_value)
    # data[key] = u'-'.join((u'codeset', codeset_type, codeset_value))


def subject_create_name(key, data, errors, context):
    data[key] = u'subject-{0}'.format(_data_lookup(('subject_code',), data))


def imdb_create_name(key, data, errors, context):
    data[key] = u'imdb-{0}'.format(_data_lookup(('product_id_new',), data))


@scheming_validator
def codeset_multiple_choice(field, schema):
    """
    Accept zero or more values from a list of choices and convert
    to a json list for storage:

    1. a list of strings, eg.:

       ["choice-a", "choice-b"]

    2. a single string for single item selection in form submissions:

       "choice-a"
    """

    def validator(key, data, errors, context):
        # if there was an error before calling our validator
        # don't bother with our validation
        if errors[key]:
            return

        codeset_type = field['codeset_type']
        codeset_choices = h.codeset_choices(codeset_type)
        value = _data_lookup(key, data)
        if value is missing:
            value = []
        elif isinstance(value, basestring):
            value = [value]
        elif isinstance(value, list):
            for element in value:
                if not isinstance(element, basestring):
                    errors[key].append(_('expecting list of strings'))
                    return
        else:
            errors[key].append(_('expecting list of strings'))
            return

        selected = set()  # store in a set to eliminate duplicates
        for element in value:
            if element in codeset_choices:
                selected.add(element)
                continue
            errors[key].append(_('unexpected choice "%s"') % element)

        if not errors[key]:
            result = json.dumps(list(selected))
            data[key] = result

    return validator
