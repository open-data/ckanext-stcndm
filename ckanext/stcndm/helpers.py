__author__ = 'matt'

import ast

import ckanapi
import ckan.logic as logic
import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckan.common import c

from ckanext.scheming.helpers import scheming_get_preset, scheming_dataset_schemas


_get_action = toolkit.get_action
_ValidationError = toolkit.ValidationError
_NotFound = toolkit.ObjectNotFound
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


def get_schema(org, dataset):
    """
    Return a dict having fields in a given org for keys and the values stored
    for that field in the tmschama organization as a dict.

    :return: dict of dicts
    """

    context = {'model': model, 'session': model.Session, 'user': c.user}

    data_dict = {'org': org, 'dataset': dataset}

    result = logic.get_action('ndm_get_schema')(context, data_dict)

    return result

def get_dataset_types():
    lc = ckanapi.LocalCKAN()
    types = lc.action.package_search(
        q='*:*',
        rows=0,
        facet='true',
        **{"facet.field": ["dataset_type"]}
    )['search_facets']['dataset_type']['items']
    schemas = scheming_dataset_schemas()
    result = {}

    for schema in schemas:
        result[schema] = {'title': schemas[schema]['catalog_type_label'], 'count': 0}

        for type in types:
            if schema == type['name']:
                result[schema]['count'] = type['count']
                break

    return sorted(result.iteritems(), key=lambda type: type[1], reverse=True)


def generate_revision_list(data_set):
    """
    :param data_set:
    :return:
    """
    # FIXME: Placeholder? What is this method for.
    # context = {'model': model, 'session': model.Session, 'user': c.user}


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

        # The revision id needs to be passed through the context rather than
        # data_dict (base CKAN quirk)
        context['revision_id'] = revision['id']

        revision_pkg = _get_action('package_show')(context, {'id': pkg_name})

        revision_extras_dict = {}

        # TODO: This will change when we move to scheming, but presently only
        # extras are important

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
                # also include added and deleted fields
                modified_fields_dict[pair[0]].append(k)

        modified_fields_dict[pair[0]].sort()

        next_record[pair[0]] = pair[1]

    return {
        'modified_fields': modified_fields_dict,
        'next_record': next_record
    }


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
            # ignore if no code is present (len < 3)
            if len(split_values) == 3:
                split_values = [value.strip() for value in split_values]
                (en_text, fr_text, code) = split_values
                self.geo_table[code] = (en_text, fr_text)

        return

    def get_by_code(self, code):

        return self.geo_table.get(code, (None, None))


class GeoSpecific:
    """
    The geo specific table (tmsgccode) is over 6k records so it shouldn't be
    loaded entirely like tmshortlist.
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
        q = (
            'zckownerorg_bi_strs:tmsgccode AND '
            'tmsgcspecificcode_bi_tmtxtm:{code}'
        ).format(code=code)

        data_dict = {'q': q, 'rows': '1'}

        response = _get_action('package_search')(self.context, data_dict)

        if response['count'] == 0:
            raise _ValidationError('Specific Geo code not found.')

        # This is very messy but the tmsgccode entries might have multiple
        # codes as in the "all provinces" entry.  If this is the case, iterate
        # through them and eliminate entries that start with "all."
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


def codeset_choices(codeset_type):
    """
    Return a dictionary of {codeset_value: title} for the codeset_type
    passed
    """
#    rc = ckanapi.RemoteCKAN('http://127.0.0.1:5000/')
    lc = ckanapi.LocalCKAN()
    results = lc.action.package_search(
        q='type:codeset',
        fq='codeset_type:' + codeset_type,
        rows=1000)
    return dict((r['codeset_value'], r['title']) for r in results['results'])


def lookup_label(field_name, field_value, lookup_type):
    """
    Given the name of a field, the value of the field, and the type of lookup
    to perform, resolve the code and return the label.

    :param field_name: The name of the field being resolved (ex: format_code).
    :param field_name: The value of the field being resolved. (ex: '33')
    :param lookup_type: The type of field being resolved (ex: codeset)
    """
    lc = ckanapi.LocalCKAN()

    default = {u'en': 'label for ' + field_value, u'fr': 'description de ' + field_value, u'found': False}

    if not field_value:
        return default

    if lookup_type == 'preset':
        preset = scheming_get_preset('ndm_{f}'.format(f=field_name))
        if not preset:
            return default

        choices = preset['choices']
        for choice in choices:
            if choice['value'] == field_value:
                return choice['label']

        return default
    elif lookup_type == 'codeset':
        results = lc.action.package_search(
            q=u'dataset_type:codeset AND codeset_type:{f} AND codeset_value:{v}'.format(
                f=field_name,
                v=field_value
            )
        )

        if not results[u'count']:
            return default

        result = results[u'results'][-1][u'title']
        if isinstance(result, basestring):
            try:
                result = ast.literal_eval(result)
            except:
                pass

        return result
    else:
        results = lc.action.package_search(
            q=u'dataset_type:{lookup_type} AND name:{lookup_type}-{field_value}'.format(
                lookup_type=lookup_type,
                field_value=field_value.lower()
            )
        )
        if not results[u'count']:
            return default

        result = results[u'results'][-1][u'title']
        if isinstance(result, basestring):
            try:
                result = ast.literal_eval(result)
            except:
                pass

        return result


def ensure_release_exists(product_id):
    """
    Ensure that a release dataset exists for the given product_id.

    :param product_id: The parent product ID.
    :type product_id: str
    """
    allowed_datasets = (
        'cube',
        'publication',
        'article',
        # FIXME: None of the below exist yet. If they're eventually added
        #        with names other than those used below this list must be
        #        updated.
        'video',
        'conference',
        'microdata',
        'generic',
        'chart',
        'indicator',
        'tableview'
    )

    lc = ckanapi.LocalCKAN()

    result = lc.action.package_search(
        q='product_id_new:{product_id}'.format(
            product_id=product_id
        ),
        rows=1,
        fl=[
            'name',
            'type',
            'owner_org'
        ]
    )

    if not result['count']:
        raise ValueError('product_id does not exist')

    result = result['results'][0]

    if result['type'] not in allowed_datasets:
        raise ValueError('{type} is not an allowed dataset type.'.format(
            type=result['type']
        ))

    release_result = lc.action.package_search(
        q='dataset_type:release AND parent_product:{pid}'.format(
            pid=result['product_id_new']
        ),
        rows=1
    )

    if release_result['count']:
        # Nothing to do, at least one release already exists.
        return

    lc.action.package_create(
        type=u'release',
        owner_org=result['owner_org'],
        release_id='001',
        parent_product=result['product_id_new'],
        publish_status_code='02',
        is_correction='0'
    )
