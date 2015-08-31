import ckan.plugins as p
from ckan.lib.base import BaseController

class ReportGeneratorController(BaseController):

    def index(self):
        return p.toolkit.render('ckanext/report_generator/index.html')