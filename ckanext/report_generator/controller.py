import ckan.plugins as p
from ckan.lib.base import BaseController, config

class ReportGeneratorController(BaseController):

    def index(self):
        from pylons import tmpl_context as c
        c.solr_url = config.get('solr_url',
                '/solr/ckan')
        c.ckan_url = config.get('ckan.site_url', '')
        return p.toolkit.render('ckanext/report_generator/index.html')