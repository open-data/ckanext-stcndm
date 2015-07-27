import json

from ckan.plugins.toolkit import missing, _
from ckanext.stcndm import helpers as h
import re
import ckan.lib.navl.dictization_functions as df

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
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    codeset_type = _data_lookup(('codeset_type',), data)
    codeset_value = _data_lookup(('codeset_value',), data).lower()
    if codeset_type and codeset_value:
        data[key] = u'codeset-{0}-{1}'.format(codeset_type, codeset_value)
    else:
        errors[key].append(_('couldn\'t find codeset_type or codeset_value'))


def subject_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    subject_code = _data_lookup(('subject_code',), data)
    if subject_code:
        data[key] = u'subject-{0}'.format((u'000000'+subject_code)[-6:])
    else:
        errors[key].append(_('couldn\'t find subject_code'))


def imdb_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    product_id_new = _data_lookup(('product_id_new',), data)
    if product_id_new:
        data[key] = u'imdb-{0}'.format(product_id_new)
    else:
        errors[key].append(_('couldn\'t find product_id_new'))


def cube_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    product_id_new = _data_lookup(('product_id_new',), data)
    if product_id_new:
        data[key] = u'cube-{0}'.format(product_id_new)
    else:
        errors[key].append(_('couldn\'t find product_id_new'))


def geodescriptor_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    geodescriptor_specific_code = _data_lookup(('geodescriptor_specific_code',), data)
    if geodescriptor_specific_code:
        data[key] = u'geodescriptor-{0}'.format(geodescriptor_specific_code.lower())
    else:
        errors[key].append(_('couldn\'t find geodescriptor_specific_code'))


def dimension_member_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    dimension_member_code = _data_lookup(('dimension_member_code',), data)
    if dimension_member_code:
        data[key] = u'dimension_member-{0}'.format(dimension_member_code)
    else:
        errors[key].append(_('couldn\'t find dimension_member_code'))


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
            else:
                errors[key].append(_('unexpected choice "%s"') % element)

        if not errors[key]:
            result = json.dumps(list(selected))
            data[key] = result

    return validator


def ndm_tag_name_validator(value, context):

    tag_name_match = re.compile('[\w \-.,:\'/()]*$', re.UNICODE)
    if not tag_name_match.match(value):
        raise df.Invalid(_('Tag "%s" must be alphanumeric characters or symbols: - _ . , : \' / ( )') % value)
    return value
