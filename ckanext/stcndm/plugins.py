
import ckan.plugins as p

class STCNDMPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IPackageController, inherit=True)

    def update_config(self, config):
        """
        Add configuration we need during startup
        """
        #p.toolkit.add_template_directory(config, "templates")
        #p.toolkit.add_public_directory(config, "static")

    def before_index(self, data_dict):
        """
        customize data sent to solr
        """
        return data_dict
