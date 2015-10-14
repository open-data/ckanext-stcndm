#!/usr/bin/env python
# encoding: utf-8
import json
import datetime

from ckan.plugins.toolkit import missing, _
from ckanext.stcndm import helpers as h
from ckan.lib.helpers import lang as lang
import re
import ckan.lib.navl.dictization_functions as df
import ckanapi


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
                errors[key].append(_('invalid encoding for "%s" value') % lang)
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


def slug_strip(slug):
    dash_index = slug.find(u'-')
    if dash_index >= 0:
        return slug[dash_index+1:]
    else:
        return slug


def codeset_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    codeset_type = _data_lookup(('codeset_type',), data)
    codeset_value = _data_lookup(('codeset_value',), data).lower()
    if codeset_type and codeset_value:
        data[key] = u'{0}-{1}'.format(codeset_type, codeset_value.lower())
    else:
        errors[key].append(_('could not find codeset_type or codeset_value'))


def format_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    parent_id = _data_lookup(('parent_id',), data)
    if not parent_id:
        errors[key].append(_('could not find parent_id of parent'))
    format_code = _data_lookup(('format_code',), data)
    if not format_code:
        errors[key].append(_('could not find format_code'))
    if errors[key]:
        return

    data[key] = u'format-{0}_{1}'.format(
        parent_id.lower(),
        format_code.zfill(2).lower()
    )


# def release_create_name(key, data, errors, context):
#     # if there was an error before calling our validator
#     # don't bother with our validation
#     if errors[key]:
#         return
#
#     if data[('release_id',)] is missing or not data[('release_id',)]:
#         lc = ckanapi.LocalCKAN()
#         query_result = lc.action.package_search(
#             q='name:release-{product_id}_{year}*'.format(
#                 product_id=data[('product_id_new',)],
#                 year=datetime.date.today().year
#             )
#         )
#         data[('release_id',)] = unicode(query_result['count'] + 1)
#
#     data[key] = (u'release-{product_id}_{year}_{release_id}'.format(
#             product_id=data[('parent_id',)],
#             year=datetime.date.today().year,
#             release_id=data[('release_id',)].zfill(3)
#         )).lower()


def subject_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    subject_code = _data_lookup(('subject_code',), data)
    if subject_code:
        data[key] = u'subject-{0}'.format(subject_code.lower())
    else:
        errors[key].append(_('could not find subject_code'))


def province_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    sgc_code = _data_lookup(('sgc_code',), data)
    if sgc_code:
        data[key] = u'province-{0}'.format(sgc_code.lower())
    else:
        errors[key].append(_('could not find sgc_code'))


def set_default_value(default_value):
    # if there was an error before calling our validator
    # don't bother with our validation

    def validator(key, data, errors, context):
        if errors[key]:
            return
        if isinstance(default_value, basestring):
            data[key] = default_value

    return validator


def survey_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    product_id_new = _data_lookup(('product_id_new',), data)
    if product_id_new:
        data[key] = u'survey-{0}'.format(product_id_new.lower())
    else:
        errors[key].append(_('could not find product_id_new'))


def correction_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    product_id_new = _data_lookup(('product_id_new',), data)
    correction_id = _data_lookup(('correction_id',), data)
    if not product_id_new:
        errors[key].append(_('could not find product_id_new'))
    elif not correction_id:
        errors[key].append(_('could not find correction_id'))
    else:
        data[key] = (u'correction-{product_id}_{correction_id}'.format(
            product_id=product_id_new,
            correction_id=correction_id
        )).lower()


def cube_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    product_id_new = _data_lookup(('product_id_new',), data)
    if product_id_new:
        data[key] = u'cube-{0}'.format(product_id_new.lower())
    else:
        errors[key].append(_('could not find product_id_new'))


def indicator_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    product_id_new = _data_lookup(('product_id_new',), data)
    if product_id_new:
        data[key] = u'indicator-{0}'.format(product_id_new.lower())
    else:
        errors[key].append(_('could not find product_id_new'))


def pumf_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    product_id_new = _data_lookup(('product_id_new',), data)
    if product_id_new:
        data[key] = u'pumf-{0}'.format(product_id_new.lower())
    else:
        errors[key].append(_('could not find product_id_new'))


def video_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    product_id_new = _data_lookup(('product_id_new',), data)
    if product_id_new:
        data[key] = u'video-{0}'.format(product_id_new.lower())
    else:
        errors[key].append(_('could not find product_id_new'))


def view_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    product_id_new = _data_lookup(('product_id_new',), data)
    if product_id_new:
        data[key] = u'view-{0}'.format(product_id_new.lower())
    else:
        errors[key].append(_('could not find product_id_new'))


def next_correction_id(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    data[key] = h.next_correction_id()


def publication_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    product_id_new = _data_lookup(('product_id_new',), data)
    if product_id_new:
        data[key] = u'publication-{0}'.format(product_id_new.lower())
    else:
        errors[key].append(_('could not find product_id_new'))


def generic_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    product_id_new = _data_lookup(('product_id_new',), data)
    if product_id_new:
        data[key] = u'generic-{0}'.format(product_id_new.lower())
    else:
        errors[key].append(_('could not find product_id_new'))


def release_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    release_id = _data_lookup(('release_id',), data)

    if not release_id:
        # Set a 300000% undocumented flag to prevent package_search from
        # rewriting fq to filter out non-public datasets (ARRRRRRRRGH)
        context['ignore_capacity_check'] = True

        lc = ckanapi.LocalCKAN(context=context)

        query_result = lc.action.package_search(
            q='name:release-{product_id}_{year}*'.format(
                product_id=data[('parent_id',)],
                year=datetime.date.today().year
            ),
            sort='release_id desc',
            rows=1
        )

        if not query_result['count']:
            # There are no existing releases, so we start from 1.
            new_release_id = '1'
        else:
            # We take the highest release and simply add one.
            last_release_id = query_result['results'][0]['release_id']
            new_release_id = str(int(last_release_id.split('_')[-1]) + 1)

        new_release_id = new_release_id.zfill(3)

        data[key] = (u'release-{product_id}_{year}_{release_id}'.format(
            product_id=data[('parent_id',)],
            year=datetime.date.today().year,
            release_id=new_release_id
        )).lower()

        data[('release_id',)] = new_release_id
    else:
        data[key] = (u'release-{product_id}_{year}_{release_id}'.format(
            product_id=data[('parent_id',)],
            year=datetime.date.today().year,
            release_id=data[('release_id',)].zfill(3)
        )).lower()


def article_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    product_id_new = _data_lookup(('product_id_new',), data)
    if product_id_new:
        data[key] = u'article-{0}'.format(product_id_new.lower())
    else:
        errors[key].append(_('could not find product_id_new'))


def daily_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    product_id_new = _data_lookup(('product_id_new',), data)
    if product_id_new:
        data[key] = u'daily-{0}'.format(product_id_new.lower())
    else:
        errors[key].append(_('could not find product_id_new'))


def conference_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    product_id_new = _data_lookup(('product_id_new',), data)
    if product_id_new:
        data[key] = u'conference-{0}'.format(product_id_new.lower())
    else:
        errors[key].append(_('could not find product_id_new'))


def service_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    product_id_new = _data_lookup(('product_id_new',), data)
    if product_id_new:
        data[key] = u'service-{0}'.format(product_id_new.lower())
    else:
        errors[key].append(_('could not find product_id_new'))


def ndm_str2boolean(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    truth_values = ['true', 'yes', 'y', '1']

    if isinstance(data[key], bool):
        return

    if data[key] is missing or data[key].lower() not in truth_values:
        data[key] = False
    else:
        data[key] = True


def geodescriptor_create_name(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return

    geodescriptor_code = _data_lookup(('geodescriptor_code',), data)
    if geodescriptor_code:
        data[key] = u'geodescriptor-{0}'.format(geodescriptor_code.lower())
    else:
        errors[key].append(_('could not find geodescriptor_code'))


def valid_parent_slug(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    if errors[key]:
        return False

    parent_slug = _data_lookup(('parent_slug',), data)
    if not parent_slug:
        errors[key].append(_('could not find parent_slug'))
        return False

    lc = ckanapi.LocalCKAN()
    query_result = lc.action.package_search(
        q='name:{0}'.format(parent_slug.lower())
    )
    if query_result['count'] < 1:
        errors[key].append(_('could not find parent_slug'))
        return False

    return True


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
        raise df.Invalid(_(
            'Tag "%s" must be alphanumeric characters or'
            ' symbols: - _ . , : \' / ( )'
        ) % value)
    return value
