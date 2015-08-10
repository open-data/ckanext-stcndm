#!/usr/bin/env python
# encoding: utf-8
import ckanapi

from ckan.logic import get_or_bust, side_effect_free
from ckan.plugins.toolkit import ValidationError, ObjectNotFound


@side_effect_free  # Allow GET access
def get_subject(context, data_dict):
    """
    :param: subjectCode: Subject Code (i.e. 13)
    :type: str

    :return: English, French and code values for given subjectCode
    :rtype: dict
    """
    lc = ckanapi.LocalCKAN(context=context)
    subject_code = get_or_bust(data_dict, 'subjectCode')
    response = lc.action.package_search(
        q='dataset_type:codeset AND extras_codeset_value:{value}'.format(
            value=subject_code
        )
    )

    if not response['count']:
        raise ObjectNotFound(
            'No subject found with subject code {subject_code}'.format(
                subject_code=subject_code
            )
        )
    elif response['count'] > 1:
        raise ValidationError((
            'Duplicate SubjectCodes have been entered '
            'in CKAN {subject_code}'
        ).format(
            subject_code
        ))
    else:
        r = response['results'][0]
        return {
            'title': r['title'],
            'subject_code': r['codeset_value']
        }


@side_effect_free
def get_top_level_subject_list(context, data_dict):
    """
    Return a list of all top level subject codes and titles.

    :return: list of all first level subjects and their values
    :rtype: list of dicts
    """
    lc = ckanapi.LocalCKAN(context=context)
    response = lc.action.package_search(
        q='dataset_type:codeset AND extras_codeset_type:content_type',
        rows=1000,
        # These are the only fields we need, but they aren't currently
        # actually passed into Solr. If we skip package_search we can
        # get a much faster query.
        fl=','.join((
            'title',
            'extras_codeset_value'
        ))
    )
    return [{
        'title': r['title'],
        'subject_code': r['codeset_value']
    } for r in response['results']]
