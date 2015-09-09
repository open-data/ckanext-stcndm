import ckan.plugins as p

class STCNDMReportGenerator(p.SingletonPlugin):

    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IConfigurer)

    def after_map(self, map):
        map.connect('report_generator', '/report-generator',
            controller='ckanext.report_generator.controller:ReportGeneratorController',
            action='index')
        return map

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_public_directory(config, 'public')
        p.toolkit.add_resource('fanstatic/ckanext/report_generator', 'ckanext_report_generator')