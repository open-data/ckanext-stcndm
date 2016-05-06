#!/usr/bin/env python
# encoding: utf-8
import json
import ckan.plugins as p
import ckanext.stcndm.logic.common as common
import ckanext.stcndm.logic.cubes as cubes
import ckanext.stcndm.logic.daily as daily
import ckanext.stcndm.logic.legacy as legacy
import ckanext.stcndm.logic.releases as releases
import ckanext.stcndm.logic.subjects as subjects
import ckanext.stcndm.logic.views as views
import ckanext.stcndm.logic.surveys as surveys
from dateutil.parser import parse
from datetime import datetime

from ckan.lib.navl.dictization_functions import _
from ckan.logic import ValidationError
from ckanext.stcndm import validators
from ckanext.stcndm import helpers
from ckanext.scheming.helpers import (
    scheming_language_text,
    scheming_get_dataset_schema
)
from helpers import lookup_label, is_dguid
import unicodedata
from ckanext.stcndm.model import geo

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


# noinspection PyMethodMayBeStatic
class STCNDMPlugin(p.SingletonPlugin):
    p.implements(p.IActions)
    p.implements(p.IConfigurer)
    p.implements(p.IPackageController, inherit=True)
    p.implements(p.IValidators)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IPackageController)
    p.implements(p.IRoutes)
    p.implements(p.IFacets)

    def update_config(self, config):
        """
        Add configuration we need during startup
        """
        p.toolkit.add_template_directory(config, "templates")
        p.toolkit.add_public_directory(config, 'public')

        config.update({
            # TODO: We can probably just make this dynamic? Are there
            #       schemas that should *not* be imported other than presets?
            'scheming.dataset_schemas': '\n'.join([
                'ckanext.stcndm:schemas/article.yaml',
                'ckanext.stcndm:schemas/chart.yaml',
                'ckanext.stcndm:schemas/codeset.yaml',
                'ckanext.stcndm:schemas/conference.yaml',
                'ckanext.stcndm:schemas/correction.yaml',
                'ckanext.stcndm:schemas/cube.yaml',
                'ckanext.stcndm:schemas/daily.yaml',
                'ckanext.stcndm:schemas/dataset.yaml',
                'ckanext.stcndm:schemas/format.yaml',
                'ckanext.stcndm:schemas/generic.yaml',
                'ckanext.stcndm:schemas/geodescriptor.yaml',
                'ckanext.stcndm:schemas/indicator.yaml',
                'ckanext.stcndm:schemas/keyword.yaml',
                'ckanext.stcndm:schemas/map.yaml',
                'ckanext.stcndm:schemas/province.yaml',
                'ckanext.stcndm:schemas/publication.yaml',
                'ckanext.stcndm:schemas/pumf.yaml',
                'ckanext.stcndm:schemas/service.yaml',
                'ckanext.stcndm:schemas/subject.yaml',
                'ckanext.stcndm:schemas/survey.yaml',
                'ckanext.stcndm:schemas/video.yaml',
                'ckanext.stcndm:schemas/view.yaml'
            ]),
            'scheming.presets': '\n'.join([
                'ckanext.scheming:presets.json',
                'ckanext.repeating:presets.json',
                'ckanext.fluent:presets.json',
                'ckanext.stcndm:schemas/presets.yaml'
            ]),
            'ckan.search.show_all_types': 'true'
        })

        from ckanext.stcndm.model.geo import setup
        setup()

    def before_index(self, data_dict):
        """
        customize data sent to solr

        :param data_dict:
        :type data_dict dict

        :returns dict
        """
        dataset_schema = scheming_get_dataset_schema(data_dict.get('type'))
        if dataset_schema is None:
            raise ValidationError((_(
                'Found no schema for following datasets:\n{dump}'.format(
                    dump=json.dumps(data_dict, indent=2, sort_keys=True)
                )
            ),))

        field_schema = dict(
            (s['field_name'], s) for s in dataset_schema['dataset_fields']
        )

        index_data_dict = data_dict.copy()
        for k in data_dict:
            if k.startswith(u'extras_'):
                index_data_dict.pop(k, None)

        authors = []
        default_date = datetime(1, 1, 1, 8, 30, 0, 0)

        validated_data_dict = json.loads(data_dict['validated_data_dict'])

        name = validated_data_dict.get(u'name')
        for item, value in validated_data_dict.iteritems():
            fs = field_schema.get(item)

            # Do not index any field that is not currently in the schema.
            if not fs:
                continue

            field_type = fs.get('schema_field_type', 'string')
            # TODO: we're not using the multivalued schema field.  Drop it?
            multivalued = fs.get('schema_multivalued', False)

            # Legacy issues numbers are non-numeric, which is problematic
            # for sorting and external tools. We can't just use a Solr
            # <copyTo> directive, as it'll fail entirely on a bad value.
            if name == 'issue_number':
                if value.isdigit():
                    index_data_dict['issue_number_int'] = int(value)

            # Fluent (multilingual) fields are really dictionaries, where
            # each key is the ISO language code, and the value the translated
            # text. We need to unpack these into individual solr fields
            # for per-language search.
            if field_type == 'fluent':
                if isinstance(value, dict):
                    index_data_dict.update(
                        (u'{0}_{1}'.format(item, k), v)
                        for k, v in value.iteritems()
                    )
                else:
                    raise ValidationError((_(
                        '{name}: Expecting a fluent dict for {item}, '
                        'instead got {value!r}'.format(
                            name=name,
                            item=item,
                            value=value
                        )
                    ), ))

            # Numeric foreign keys that need to be looked up to retrieve
            # their multilingual labels for searching.
            elif field_type == u'code':
                index_data_dict[unicode(item)] = value

                # These codes can refer to a codeset (a dataset of type
                # 'codeset' with a particular key), a preset (a hardcoded
                # value in a Scheming schema), or another dataset (lookup).
                lookup_type = fs.get(u'lookup', '')
                if lookup_type == u'codeset':
                    lookup = fs.get(u'codeset_type', '')
                elif lookup_type == u'preset':
                    lookup = fs.get(u'preset', '')[4:]
                else:
                    lookup = fs.get(u'lookup', '')

                if not lookup:
                    raise ValidationError((_(
                        '{name}: unable to determine lookup '
                        'for {item}'.format(
                            name=name,
                            item=item
                        )
                    ), ))

                if isinstance(value, list):
                    for value_to_lookup in value:
                        if not value_to_lookup:
                            continue

                        desc = lookup_label(
                            lookup,
                            value_to_lookup,
                            lookup_type
                        )

                        for k, v in desc.iteritems():
                            if v and not k == u'found':
                                n = u'{item}_desc_{key}'.format(
                                    item=item,
                                    key=k
                                )
                                index_data_dict.update(
                                    {n: index_data_dict.get(n, []) + [v]}
                                )

                else:
                    desc = lookup_label(lookup, value, lookup_type)

                    index_data_dict.update((
                        u'{item}_desc_{key}'.format(
                            item=item,
                            key=k
                        ), v)
                        for k, v in desc.iteritems() if v and not k == u'found'
                    )
                if item == u'geodescriptor_codes':
                    index_data_dict[u'dguid_codes'] = \
                        list(index_data_dict[u'geodescriptor_codes'])
                    # append dguids from the datastore
                    for dguid_pkg_id in geo.get_geodescriptors_for_package(
                            validated_data_dict[u'product_id_new']):
                        index_data_dict[u'dguid_codes'].append(
                                helpers.get_dguid_from_pkg_id(dguid_pkg_id))
                    # strip the vintages from dguids to get geodescriptors
                    index_data_dict[u'geodescriptor_codes'] = \
                        [g[4:] if is_dguid(g) else g
                         for g in index_data_dict[u'dguid_codes'] if g]
            elif field_type == 'date':
                try:
                    date = parse(value, default=default_date)
                    index_data_dict[unicode(item)] = unicode(
                        date.isoformat()[:19] + u'Z'
                    )
                except ValueError:
                    continue
            elif item.endswith('_authors'):
                index_data_dict[unicode(item)] = value
                authors.extend(value)
            else:
                index_data_dict[unicode(item)] = value

            if authors:
                index_data_dict['authors'] = authors
                index_data_dict['authors_initials'] = list(
                    set(
                        [strip_accents(i[0]).upper() for i in authors]
                    )
                )

        return index_data_dict

    def after_create(self, context, data):
        if 'model' in context:
            # We need to force a commit to get the metadata_modified
            # and metadata_created columns. It is *not* enough for us to
            # simply set these ourselves. This is caused by after_create
            # being called long before creation is actually complete.
            context['model'].repo.commit()

        if context.get('__cloning'):
            # We don't want to call this while we're cloning, or we'll
            # end up with duplicate release records.
            return

        product_id_new = data.get('product_id_new')
        if data['type'] == 'format':
            product_id_new = data.get('format_id')

        if not product_id_new:
            return

        helpers.ensure_release_exists(product_id_new, context=context)

    def get_actions(self):
        # Some Java web clients require the web service to use Pascal Case
        return {
            "GetAutocomplete": common.get_autocomplete,
            "GetInternalAuthors": common.get_internal_authors,
            "DeleteProduct": common.delete_product,
            "EnsureReleaseExists": releases.ensure_release_exists,
            "GetBookableProducts": daily.get_bookable_releases,
            "GetCubeList": cubes.get_cube_list_by_subject,
            "GetCube": cubes.get_cube,
            "UpdateCube": cubes.update_cube,
            "GetNextCubeId": cubes.get_next_cube_id,
            "GetNextNonDataProductId": common.get_next_non_data_product_id,
            "CreateOrUpdateCubeRelease": cubes.create_or_update_cube_release,
            "GetThemes": daily.get_themes,
            "GetDailyList": daily.get_daily_list,
            "GetDefaultViews": daily.get_default_views,
            "GetDerivedProductList": common.get_derived_product_list,
            "GetFormatDescription": common.get_format_description,
            "GetLastPublishStatus": common.get_last_publish_status,
            "GetNextProductId": common.get_next_product_id,
            "GetNextLegacyArticleId": legacy.get_next_legacy_article_id,
            "GetNextLegacyProductId": legacy.get_next_legacy_product_id,
            "GetProduct": common.get_product,
            "GetProductIssueArticles": daily.get_product_issue_articles,
            "GetProductIssues": daily.get_product_issues,
            "GetProductType": common.get_product_type,
            "GetReleasesForProduct": releases.get_releases_for_product,
            "GetSubject": subjects.get_subject,
            "GetSubjectList": subjects.get_top_level_subject_list,
            "GetSurveySubjectCodes": surveys.get_survey_subject_codes,
            "GetUpcomingReleases": common.get_upcoming_releases,
            "GetIssuesByPubStatus": common.get_issues_by_pub_status,
            "GetProductFormats": daily.get_product_formats,
            "GetProductUrl": common.get_product_url,
            "GetProductsBySurvey": surveys.get_products_by_survey,
            "PurgeDataset": common.purge_dataset,
            "RegisterCube": cubes.register_cube,
            "RegisterDaily": daily.register_daily,
            "RegisterDataProduct": common.register_data_product,
            "RegisterNonDataProduct": common.register_non_data_product,
            "RegisterLegacyNonDataProduct":
                legacy.register_legacy_non_data_product,
            "RegisterProduct": common.register_data_product,
            "RegisterSurvey": surveys.register_survey,
            "UpdateDefaultView": views.update_default_view,
            "UpdateReleaseDateAndStatus":
                common.update_release_date_and_status,
            "UpdateProductGeo": common.update_product_geo,
            "UpdatePublishingStatus": common.update_last_publish_status,
            "GetDatasetSchema": common.get_dataset_schema,
            "GetGroupSchema": common.get_group_schema,
            "GetSurveyCodesets": surveys.get_survey_codesets,
            "GetSubjectCodesets": subjects.get_subject_codesets,
            "GetProductsByFRC": daily.get_products_by_frc,
            "ConsumeTransactionFile": releases.consume_transaction_file
        }

    def get_validators(self):
        return {
            "apply_archive_rules": validators.apply_archive_rules,
            "archive_children_of_cube": validators.archive_children_of_cube,
            "codeset_create_name": validators.codeset_create_name,
            "codeset_multiple_choice": validators.codeset_multiple_choice,
            "correction_create_name": validators.correction_create_name,
            "create_product_id": validators.create_product_id,
            "daily_create_name": validators.daily_create_name,
            "set_default_value": validators.set_default_value,
            "format_create_name": validators.format_create_name,
            "format_create_id": validators.format_create_id,
            "geodescriptor_create_name": validators.geodescriptor_create_name,
            "keyword_create_name": validators.keyword_create_name,
            "ndm_str2boolean": validators.ndm_str2boolean,
            "ndm_tag_name_validator": validators.ndm_tag_name_validator,
            "ndm_child_inherits_value": validators.ndm_child_inherits_value,
            "province_create_name": validators.province_create_name,
            "product_create_name": validators.product_create_name,
            "shortcode_validate": validators.shortcode_validate,
            "shortcode_output": validators.shortcode_output,
            "subject_create_name": validators.subject_create_name,
            "survey_create_name": validators.survey_create_name,
            "repeating_text_delimited": validators.repeating_text_delimited,
        }

    def get_helpers(self):
        return {
            "codeset_choices": helpers.codeset_choices,
            "lookup_label": helpers.lookup_label,
            "get_dataset_types": helpers.get_dataset_types,
            "get_parent_content_types": helpers.get_parent_content_types,
            "set_previous_issue_archive_date":
                helpers.set_previous_issue_archive_date,
            'ensure_release_exists': helpers.ensure_release_exists,
            'get_parent_dataset': helpers.get_parent_dataset,
            'get_child_datasets': helpers.get_child_datasets,
            'x2list': helpers.x2list,
            'set_related_id': helpers.set_related_id,
            'changes_since': helpers.changes_since,
            'get_geolevel': helpers.get_geolevel,
            'get_dguid_from_pkg_id': helpers.get_dguid_from_pkg_id,
        }

    def before_view(self, pkg_dict):
        """
        Ensure that (if available) the correct language strings
        are used for core CKAN fields.
        """
        fields_to_fluent = (
            u'title',
            u'notes'
        )

        for field in fields_to_fluent:
            if field in pkg_dict and isinstance(pkg_dict[field], dict):
                pkg_dict[field] = scheming_language_text(pkg_dict[field])

        return pkg_dict

    def before_map(self, map):
        map.connect(
            'clone',
            '/dataset/clone/{ds_id}',
            controller=(
                'ckanext.stcndm.controllers.clone'
                ':CloneDatasetController'
            ),
            action='clone'
        )

        map.connect(
            'child_dataset',
            '/dataset/{ds_id}/child/{ds_type}/new',
            controller=(
                'ckanext.stcndm.controllers.child_dataset'
                ':ChildDatasetController'
            ),
            action='new'
        )

        map.connect(
            'solr_proxy',
            '/solr/select',
            controller=(
                'ckanext.stcndm.controllers.solr_proxy'
                ':SolrProxyController'
            ),
            action='select'
        )

        map.connect(
            'schema_to_xl',
            '/schema_to_xl/dump',
            controller=(
                'ckanext.stcndm.controllers.schema_to_xl'
                ':SchemaToXlController'
            ),
            action='dump'
        )

        return map

    def after_map(self, map):
        # Required since we implement IRoutes.
        return map

    def dataset_facets(self, facets_dict, package_type):
        return facets_dict

    def organization_facets(self, facets_dict, organization_type,
                            package_type):
        # We always want the dataset type selector to appear.
        # Currently, groups, organizations, licence type, etc... do not
        # apply to ndm, so lets clear the default fields as well.
        facets_dict.clear()
        facets_dict['dataset_type'] = _('Dataset Type')
        return facets_dict

    def group_facets(self, facets_dict, group_type, package_type):
        return facets_dict
