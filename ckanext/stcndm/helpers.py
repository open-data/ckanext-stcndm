__author__ = 'matt'

# import ckan
# import ckan.plugins as p
# import ckan.exceptions
# from ckan.common import (_, ungettext, g, request, session, json, OrderedDict)
import ckan.logic as logic
import ckan.model as model
import ckan.plugins.toolkit as toolkit

from ckan.common import c

# noinspection PyUnresolvedReferences
_get_action = toolkit.get_action
# noinspection PyUnresolvedReferences
_ValidationError = toolkit.ValidationError
# noinspection PyUnresolvedReferences
_NotFound = toolkit.ObjectNotFound
# noinspection PyUnresolvedReferences
_NotAuthorized = toolkit.NotAuthorized


def dict_list2dict(dict_list):
    d = dict()

    for dict_item in dict_list:
        d[dict_item['key']] = dict_item['value']

    return d


def dict2dict_list(dictionary):
    dl = list()

    for key in dictionary.keys():
        dl.append({'key': key, 'value': dictionary[key]})

    return dl


def get_dropdowns():
    """
    Return a dict having fields with dropdown menus for keys and lists of dicts
    of possible values for the dropdowns as values.


    :return: dict of list of dicts
    """
    context = {'model': model, 'session': model.Session, 'user': c.user}

    data_dict = {}

    result = logic.get_action('ndm_get_dropdowns')(context, data_dict)

    return result


def get_schema(org, dataset):
    """
    Return a dict having fields in a given org for keys and the values stored for that field in the tmschama
    organization as a dict.

    :return: dict of dicts
    """

    context = {'model': model, 'session': model.Session, 'user': c.user}

    data_dict = {'org': org, 'dataset': dataset}

    result = logic.get_action('ndm_get_schema')(context, data_dict)

    return result


def generate_revision_list(data_set):
    """

    :param data_set:

    :return:
    """

    context = {'model': model, 'session': model.Session, 'user': c.user}


# TODO: rename this
def show_fields_changed_between_revisions(pkg_name, pkg_revisions):
    """
    :param pkg_name: name or id of package
    :type pkg_name: str
    :param pkg_revisions: revision details
    :type pkg_revisions: list of dicts

    :return: string
    """

    context = {'model': model, 'session': model.Session, 'user': c.user}

    revisions_dict = {}

    revision_order = []
    for revision in pkg_revisions:

        # The revision id needs to be passed through the context rather than data_dict (base CKAN quirk)
        context['revision_id'] = revision['id']

        revision_pkg = _get_action('package_show')(context, {'id': pkg_name})

        revision_extras_dict = {}

        # TODO: This will change when we move to scheming, but presently only extras are important

        for extra in revision_pkg['extras']:
            revision_extras_dict[extra['key']] = extra['value']

        revisions_dict[revision['id']] = revision_extras_dict

        revision_order.append(revision['id'])

    def _pairs(lst):
        i = iter(lst)
        prev = i.next()
        for item in i:
            yield prev, item
            prev = item

    revisions_to_compare = _pairs(revision_order)

    next_record = {}
    modified_fields_dict = {}

    for pair in revisions_to_compare:

        new_dict = revisions_dict[pair[0]]
        old_dict = revisions_dict[pair[1]]

        modified_fields_dict[pair[0]] = []
        for k, v in new_dict.iteritems():

            try:
                if old_dict[k] != new_dict[k]:
                    modified_fields_dict[pair[0]].append(k)
            except KeyError:
                modified_fields_dict[pair[0]].append(k)  # also include added and deleted fields

        modified_fields_dict[pair[0]].sort()

        next_record[pair[0]] = pair[1]

    return {'modified_fields': modified_fields_dict, 'next_record': next_record}


class GeoLevel:
    def __init__(self, context):
        self.geo_table = {}

        self.get_geolevel_table(context)

    def get_geolevel_table(self, context):

        q = 'zckownerorg_bi_strs:tmshortlist'
        fq = 'tmdroplfld_bi_tmtxtm:extras_geolevel_en_txtm'

        data_dict = {'q': q, 'fq': fq, 'rows': '1000'}

        response = _get_action('package_search')(context, data_dict)

        for result in response['results']:
            result_dict = {}

            for extra in result['extras']:
                result_dict[extra['key']] = extra['value']

            split_values = result_dict['tmdroplopt_bi_tmtxtm'].split('|')
            if len(split_values) == 3:                                      # ignore if no code is present (len < 3)
                split_values = [value.strip() for value in split_values]
                (en_text, fr_text, code) = split_values
                self.geo_table[code] = (en_text, fr_text)

        return

    def get_by_code(self, code):

        return self.geo_table.get(code, (None, None))


class GeoSpecific:
    """
    The geo specific table (tmsgccode) is over 6k records so it shouldn't be loaded entirely like tmshortlist.
    Code descriptions will be searched when required.

    """
    def __init__(self, context):
        self.context = context

    def get_by_code(self, code):
        """
        :param code: code for specific geo code
        :type code: str

        :return: tuple of english and french descriptions
        """
        q = 'zckownerorg_bi_strs:tmsgccode AND tmsgcspecificcode_bi_tmtxtm:{code}'.format(code=code)

        data_dict = {'q': q, 'rows': '1'}

        response = _get_action('package_search')(self.context, data_dict)

        if response['count'] == 0:
            raise _ValidationError('Specific Geo code not found.')

        # This is very messy but the tmsgccode entries might have multiple codes as in the
        # "all provinces" entry.  If this is the case, iterate through them and eliminate
        # entries that start with "all."
        if response['count'] > 1:
            result = None
            for res in response['results']:
                for extra in res['extras']:
                    if extra['key'] == 'tmsgccode_bi_tmtxtm':
                        if not extra['value'].lower().startswith('all'):
                            result = res
                        break
                if result:
                    break
        else:
            result = response['results'][0]

        if result:
            result_dict = {}

            for extra in result['extras']:
                result_dict[extra['key']] = extra['value']

            en_text = result_dict.get('tmsgcname_en_tmtxtm', '')
            fr_text = result_dict.get('tmsgcname_fr_tmtxtm', '')
        else:
            en_text = fr_text = None

        return en_text, fr_text
