import ckan.plugins as p
from ckan.plugins.toolkit import c
from ckan.lib.base import BaseController, config

class ReportGeneratorController(BaseController):

    c.solr_url = config.get('solr_url',
            'http://127.0.0.1:8983/solr/ckan')
    c.ckan_url = config.get('ckan.site_url', '')

    def index(self):
        return p.toolkit.render('ckanext/report_generator/index.html')