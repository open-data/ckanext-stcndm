
import ckan.plugins as p
import ckanext.stcndm.logic.codesets as codesets
import ckanext.stcndm.logic.common as common
import ckanext.stcndm.logic.cubes as cubes
import ckanext.stcndm.logic.daily as daily
import ckanext.stcndm.logic.publications as pubs
import ckanext.stcndm.logic.subjects as subjects
import ckanext.stcndm.logic.views as views

from ckanext.stcndm import validators
from ckanext.stcndm import helpers

class STCNDMPlugin(p.SingletonPlugin):
    p.implements(p.IActions)
    p.implements(p.IConfigurer)
    p.implements(p.IPackageController, inherit=True)
    p.implements(p.IValidators)
    p.implements(p.ITemplateHelpers)

    def update_config(self, config):
        """
        Add configuration we need during startup
        """
        p.toolkit.add_template_directory(config, "templates")
        p.toolkit.add_public_directory(config, 'public')

    def before_index(self, data_dict):
        """
        customize data sent to solr
        """
        return data_dict

    def get_actions(self):
        # Some Java web clients require the web service to use Pascal Case
        return {
            "DeleteProduct": common.delete_product,
            "GetBookableReleases": daily.get_bookable_releases,
            "GetCubeList": cubes.get_cube_list_by_subject,
            "GetDailyList": daily.get_daily_list,
            "GetDefaultViews": daily.get_default_views,
            "GetDerivedProductList": common.get_derived_product_list,
            "GetFieldList": common.get_field_list,
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
            "PurgeDataset": common.purge_dataset,
            "RegisterCube": cubes.register_cube,
            "RegisterDaily": daily.register_daily,
            "RegisterProduct": common.tv_register_product,
            "UpdateDefaultView": views.update_default_view,
            "UpdateProductGeo": common.update_product_geo,
            "UpdatePublishingStatus": common.update_last_publish_status,
        }

    def get_validators(self):
        return {
            "shortcode_validate": validators.shortcode_validate,
            "shortcode_output": validators.shortcode_output,
            "codeset_create_name": validators.codeset_create_name,
            "codeset_multiple_choice": validators.codeset_multiple_choice,
            "subject_create_name": validators.subject_create_name,
            "geodescriptor_create_name": validators.geodescriptor_create_name,
            "imdb_create_name": validators.imdb_create_name,
            "ndm_tag_name_validator": validators.ndm_tag_name_validator,
        }

    def get_helpers(self):
        return {
            "codeset_choices": helpers.codeset_choices,
        }
