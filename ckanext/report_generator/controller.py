import ckan.plugins as p
from ckan.plugins.toolkit import c
from ckan.lib.base import BaseController, config

class ReportGeneratorController(BaseController):

    SOLR_URL = config.get('solr_url',
            'http://127.0.0.1:8983/solr/ckan')
    CKAN_URL = config.get('ckan.site_url', '')

    def index(self):
        c.solr_url = self.SOLR_URL
        c.ckan_url = self.CKAN_URL

        return p.toolkit.render('ckanext/report_generator/index.html')