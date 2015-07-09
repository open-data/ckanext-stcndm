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

    q = {'q': 'tmtaxsubjcode_bi_tmtxtm:{subject_code}'.format(subject_code=subject_code)}

    result = _get_action('package_search')(context, q)

    count = result['count']

    if count == 0:
        raise _NotFound('No subject found with subject code {0}'.format(subject_code))
    if count > 1:
        raise _ValidationError('Duplicate SubjectCodes have been entered in CKAN {0}'.format(subject_code))
    else:
        desired_extras = ['tmtaxsubj_en_tmtxtm', 'tmtaxsubj_fr_tmtxtm', 'tmtaxsubjcode_bi_tmtxtm']

        output = {}

        for extra in result['results'][0]['extras']:
            if extra['key'] in desired_extras:
                output[extra['key']] = extra['value']

        return output


@logic.side_effect_free
def get_top_level_subject_list(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Return a list of all top level subject codes and French/English titles.

    Please note that this implementation will be speedier shortly.

    :return: list of all first level subjects and their values
    :rtype: list of dicts
    """
    q = {'q': 'zckownerorg_bi_strs:tmtaxonomy',
         'rows': '1000'}  # TODO: This will need to be sped up, but Solr doesn't allow wildcard-only queries

    response = _get_action('package_search')(context, q)

    top_level_subject_list = []

    for result in response['results']:
        subject_dict = {}
        update = False
        for extra in result['extras']:
            if extra['key'] == 'tmtaxsubjcode_bi_tmtxtm' and len(extra['value']) == 2:
                update = True
                subject_dict['subject_code'] = extra['value']
#            elif extra['key'] == 'tmtaxsubj_en_tmtxtm':
#                subject_dict['subject_en_txtm'] = extra['value']
#            elif extra['key'] == 'tmtaxsubj_fr_tmtxtm':
#                subject_dict['subject_fr_txtm'] = extra['value']
        if update:
            top_level_subject_list.append(subject_dict)

    return top_level_subject_list
