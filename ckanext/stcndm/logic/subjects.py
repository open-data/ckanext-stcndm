#!/usr/bin/env python
# encoding: utf-8
import textwrap

import ckanapi

from ckan import logic
from ckan.logic import get_or_bust, side_effect_free
from ckan.plugins.toolkit import ValidationError, ObjectNotFound


@side_effect_free
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
        q='dataset_type:subject AND subject_code:{value}'.format(
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
            'subject_code': r['subject_code']
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
        q='dataset_type:subject AND subject_code:??',
        rows=1000,
        # These are the only fields we need, but they aren't currently
        # actually passed into Solr. If we skip package_search we can
        # get a much faster query.
        fl=','.join((
            'title',
            'subject_code'
        ))
    )
    return [{
        'title': r['title'],
        'subject_code': r['subject_code']
    } for r in response['results']]


@logic.side_effect_free
def get_subject_codesets(context, data_dict):
    """
    Returns all subject codesets.

    :param limit: Number of results to return.
    :type limit: int
    :param start: Number of results to skip.
    :type start: int

    :rtype: list of dicts
    """
    lc = ckanapi.LocalCKAN(context=context)

    # Sort would perform better, but this will be easier
    # for client to implement.
    limit = int(logic.get_or_bust(data_dict, 'limit'))
    start = int(logic.get_or_bust(data_dict, 'start'))

    results = lc.action.package_search(
        q='dataset_type:subject',
        rows=limit,
        start=start,
        fl=(
            'name',
            'title'
        )
    )

    def _massage(s):
        chunked = textwrap.wrap(s['subject_code'], 2)
        return (
            chunked[-1],
            chunked[-2] if len(chunked) > 1 else None,
            s['title']
        )

    return {
        'count': results['count'],
        'limit': limit,
        'start': start,
        'results': [{
            'subject_code': rr[0],
            'parent_subject_code': rr[1],
            'title': rr[2],
        } for rr in (_massage(r) for r in results['results'])]
    }
