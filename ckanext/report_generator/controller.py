import ckan.plugins as p
from ckan.plugins.toolkit import c
from ckan.lib.base import BaseController, config
from ckan.lib.helpers import url_for_static


class ReportGeneratorController(BaseController):

    CKAN_URL = url_for_static('/')[:-1]
    SOLR_URL = url_for_static('/solr')
    SITE_ID = config.get('ckan.site_id', '')

    def index(self):
        c.solr_url = self.SOLR_URL
        c.ckan_url = self.CKAN_URL
        c.site_id = self.SITE_ID

        return p.toolkit.render('ckanext/report_generator/index.html')
