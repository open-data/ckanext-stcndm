__author__ = 'Statistics Canada'

import ckan.logic as logic
import ckan.plugins.toolkit as toolkit

_get_or_bust = logic.get_or_bust
# noinspection PyUnresolvedReferences
_get_action = toolkit.get_action
# noinspection PyUnresolvedReferences
_ValidationError = toolkit.ValidationError
# noinspection PyUnresolvedReferences
_NotFound = toolkit.ObjectNotFound
# noinspection PyUnresolvedReferences
_NotAuthorized = toolkit.NotAuthorized


@logic.side_effect_free  # Allow GET access
def get_subject(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    :param: subjectCode: Subject Code (i.e. 13)
    :type: str

    :return: English, French and code values for given subjectCode
    :rtype: dict
    """

    subject_code = data_dict['subjectCode']

    q = {
        'q': 'tmtaxsubjcode_bi_tmtxtm:{subject_code}'.format(
            subject_code=subject_code
        )
    }

    result = _get_action('package_search')(context, q)

    count = result['count']

    if count == 0:
        raise _NotFound(
            'No subject found with subject code {0}'.format(subject_code)
        )
    if count > 1:
        raise _ValidationError(
            'Duplicate SubjectCodes have been entered in CKAN {0}'.format(
                subject_code
            )
        )
    else:
        desired_extras = [
            'tmtaxsubj_en_tmtxtm',
            'tmtaxsubj_fr_tmtxtm',
            'tmtaxsubjcode_bi_tmtxtm'
        ]

        output = {}

        for extra in result['results'][0]['extras']:
            if extra['key'] in desired_extras:
                output[extra['key']] = extra['value']

        return output


@logic.side_effect_free
def get_top_level_subject_list(context, data_dict):
    """
    Return a list of all top level subject codes and titles.

    :return: list of all first level subjects and their values
    :rtype: list of dicts
    """
    response = _get_action('package_search')(context, {
        'q': 'dataset_type:codeset AND extras_codeset_type:content_type',
        'rows': 1000,
        # These are the only fields we need, but they aren't currently
        # actually passed into Solr. If we skip package_search we can
        # get a much faster query.
        'fl': ','.join((
            'title',
            'extras_codeset_value'
        ))
    })
    return [{
        'title': r['title'],
        'subject_code': r['codeset_value']
    } for r in response['results']]
