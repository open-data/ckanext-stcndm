#!/usr/bin/env python
# encoding: utf-8
import json
import ckan.plugins as p
import ckanext.stcndm.logic.common as common
import ckanext.stcndm.logic.cubes as cubes
import ckanext.stcndm.logic.daily as daily
import ckanext.stcndm.logic.subjects as subjects
import ckanext.stcndm.logic.views as views
import ckanext.stcndm.logic.surveys as surveys
import datetime
from dateutil.parser import parse

from ckan.plugins.toolkit import _
from ckan.plugins.toolkit import ValidationError
from ckanext.stcndm import validators
from ckanext.stcndm import helpers
from ckanext.scheming.helpers import (
    scheming_language_text,
    scheming_get_dataset_schema
)
from helpers import lookup_label


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
                'ckanext.stcndm:schemas/codeset.yaml',
                'ckanext.stcndm:schemas/conf_service.yaml',
                'ckanext.stcndm:schemas/corrections.yaml',
                'ckanext.stcndm:schemas/cube.yaml',
                'ckanext.stcndm:schemas/daily.yaml',
                'ckanext.stcndm:schemas/geodescriptor.yaml',
                'ckanext.stcndm:schemas/indicator.yaml',
                'ckanext.stcndm:schemas/issue.yaml',
                'ckanext.stcndm:schemas/publication.yaml',
                'ckanext.stcndm:schemas/pumf.yaml',
                'ckanext.stcndm:schemas/subject.yaml',
                'ckanext.stcndm:schemas/view.yaml',
                'ckanext.stcndm:schemas/survey.yaml'
            ]),
            'scheming.presets': '\n'.join([
                'ckanext.scheming:presets.json',
                'ckanext.fluent:presets.json',
                'ckanext.stcndm:schemas/presets.yaml'
            ])
        })

    # def _lookup_label(self, lookup_key, value, lookup_type):
    #
    #     default = {u'en': u'label for ' + value, u'fr': u'label pour ' + value}
    #     try:
    #         label = lookup_label(lookup_key, value, lookup_type)
    #     except Exception:
    #         label = default
    #
    #     if 'fr' not in label:
    #         label['fr'] = u'description pour ' + value
    #
    #     if 'en' not in label:
    #         label['en'] = u'label for ' + value
    #
    #     return label

    def before_index(self, data_dict):
        """
        customize data sent to solr
        """
        bogus_date = datetime.datetime(1, 1, 1)
        dataset_schema = scheming_get_dataset_schema(
            data_dict.get('type', 'unknown')
        )
        if dataset_schema is None:
            raise ValidationError(
                'Found no schema for following dataset :\n{dump}'.format(
                    dump=json.dumps(data_dict, indent=2)
                )
            )

        # iterate through dataset fields defined in schema
        field_schema = dict()
        for dataset_field in dataset_schema['dataset_fields']:
            d = dataset_field
            field_schema[d['field_name']] = d

        index_data_dict = {}
        # drop extras fields
        for dict_key in data_dict:
            if not dict_key.startswith('extras_'):
                index_data_dict[dict_key] = data_dict[dict_key]
        # iterate through validated data_dict fields and modify as needed
        validated_data_dict = json.loads(data_dict['validated_data_dict'])
        for item in validated_data_dict.keys():
            value = validated_data_dict[item]
            if not value and item in index_data_dict:
                index_data_dict.pop(item)
                continue
            fs = field_schema.get(item, None)
            # ignore all fields not currently in the schema
            if not fs:
                continue

            field_type = fs.get('schema_field_type', 'string')
            multivalued = fs.get('schema_multivalued', False)

            if field_type == 'fluent':
                for key in value.keys():
                    label = '{item}_{key}'.format(
                        item=item,
                        key=key
                    )
                    index_data_dict[label] = value[key]

            # for code type, the en/fr labels need to be looked up
            # and sent to Solr
            elif field_type == 'code':
                lookup_type = fs.get('lookup', '')
                if lookup_type == 'codeset':
                    lookup = fs.get('codeset_type', '')
                elif lookup_type == 'preset':
                    lookup = fs.get('preset', '')[4:]
                else:
                    lookup = fs.get('lookup', '')
                if lookup and value:
                    label_en = '{item}_desc_en'.format(
                        item=item
                    )
                    label_fr = '{item}_desc_fr'.format(
                        item=item
                    )
                    if multivalued:
                        desc_en = []
                        desc_fr = []
                        for v in value:
                            if not v:
                                continue
                            desc = lookup_label(lookup, v, lookup_type)
                            desc_en.append(desc['en'])
                            desc_fr.append(desc['fr'])

                        index_data_dict[str(item)] = value

                        index_data_dict[label_en] = desc_en
                        index_data_dict[label_fr] = desc_fr
                    else:
                        desc = lookup_label(lookup, value, lookup_type)
                        index_data_dict[label_en] = desc['en']
                        index_data_dict[label_fr] = desc['fr']
            elif item.endswith('_date'):
                if value:
                    try:
                        date = parse(value, default=bogus_date)
                        if date != bogus_date:
                            index_data_dict[item] = date.isoformat() + 'Z'
                    except ValueError:
                        continue
            else:  # all other field types
                if multivalued:
                    index_data_dict[str(item)] = value
                else:
                    index_data_dict[str(item)] = value

        return index_data_dict

    def get_actions(self):
        # Some Java web clients require the web service to use Pascal Case
        return {
            "DeleteProduct": common.delete_product,
            "GetBookableReleases": daily.get_bookable_releases,
            "GetCubeList": cubes.get_cube_list_by_subject,
            "GetCube": cubes.get_cube,
            "GetNextCubeId": cubes.get_next_cube_id,
            "GetDailyList": daily.get_daily_list,
            "GetDefaultViews": daily.get_default_views,
            "GetDerivedProductList": common.get_derived_product_list,
            "GetFormatDescription": common.get_format_description,
            "GetLastPublishStatus": common.get_last_publish_status,
            "GetNextProductId": common.get_next_product_id,
            "GetProduct": common.get_product,
            "GetProductIssueArticles": daily.get_product_issue_articles,
            "GetProductIssues": daily.get_product_issues,
            "GetProductType": common.get_product_type,
            "GetSubject": subjects.get_subject,
            "GetSubjectList": subjects.get_top_level_subject_list,
            "GetSurveys": daily.get_surveys,
            "GetThemes": daily.get_themes,
            "GetUpcomingReleases": common.get_upcoming_releases,
            "GetIssuesByPubStatus": common.get_issues_by_pub_status,
            "PurgeDataset": common.purge_dataset,
            "RegisterCube": cubes.register_cube,
            "RegisterDaily": daily.register_daily,
            "RegisterProduct": common.tv_register_product,
            "UpdateDefaultView": views.update_default_view,
            "UpdateProductGeo": common.update_product_geo,
            "UpdatePublishingStatus": common.update_last_publish_status,
            "GetDatasetSchema": common.get_dataset_schema,
            "GetGroupSchema": common.get_group_schema,
            "GetSurveyCodesets": surveys.get_survey_codesets,
            "GetSubjectCodesets": subjects.get_subject_codesets
        }

    def get_validators(self):
        return {
            "shortcode_validate": validators.shortcode_validate,
            "shortcode_output": validators.shortcode_output,
            "codeset_multiple_choice": validators.codeset_multiple_choice,
            "codeset_create_name": validators.codeset_create_name,
            "subject_create_name": validators.subject_create_name,
            "geodescriptor_create_name": validators.geodescriptor_create_name,
            "survey_create_name": validators.survey_create_name,
            "cube_create_name": validators.cube_create_name,
            "view_create_name": validators.view_create_name,
            "publication_create_name": validators.publication_create_name,
            "issue_create_name": validators.issue_create_name,
            "article_create_name": validators.article_create_name,
            "ndm_tag_name_validator": validators.ndm_tag_name_validator,
            "ndm_str2boolean": validators.ndm_str2boolean,
        }

    def get_helpers(self):
        return {
            "codeset_choices": helpers.codeset_choices,
            "lookup_label": helpers.lookup_label
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
            'list',
            '/api/current/list',
            controller=(
                'ckanext.stcndm.controllers.api_ext'
                ':APIExtController'
            ),
            action='list'
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
