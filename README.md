# ckanext-stcndm #


A CKAN Extension used for Statistics Canada's New Dissemination Model project.

## Prerequisites ##

 - Python 2.6 or 2.7
 - pip
 - virtualenv
 - Postgres 9.4
 - Apache Solr 5.3.1
 - libgeos
 - Git

## Requirements ##

**CKAN Related**

Project | Github group/repo | Branch
------- | ----------------- | ------
ckan    | [open-data/cka](open-data/ckan "open-data/ckan") | release-v2.4-ndm
ckanapi | [ckan/ckanapi](https://github.com/ckan/ckanapi "ckan/ckanapi") | master
ckanext-scheming | [ckan/ckanext-scheming](https://github.com/ckan/ckanext-scheming "ckan/ckanext-scheming") | master
ckanext-fluent | [ckan/ckanext-fluent](https://github.com/ckan/ckanext-fluent "ckan/ckanext-fluent") | master
ckanext-repeating | [open-data/ckanext-repeating](https://github.com/open-data/ckanext-repeating "open-data/ckanext-repeating") | master
ckanext-autodoc | [open-data/ckanext-autodoc](https://github.com/open-data/ckanext-autodoc "open-data/ckanext-autodoc") | master
ckanext-wet-boew | [open-data/ckanext-wet-boew](https://github.com/open-data/ckanext-wet-boew "open-data/ckanext-wet-boew") | wet4-scheming

**WET-BOEW Related**

- [WET-BOEW 4.0.18](https://github.com/wet-boew/wet-boew-cdn/archive/v4.0.18.tar.gz "WET-BOEW 4.0.18")
- [Theme-GC-Intranet 4.0.18](https://github.com/wet-boew/themes-cdn/archive/v4.0.18-theme-gc-intranet.tar.gz "Theme-GC-Intranet 4.0.18")

## Installation ##

This installation was based on RedHat-based operating system and is for setting up a Development Environment.

1. Create a python virtual environment and activate it.
2. Create a project directory and change to it.

    *This guide assumes you are always at the root of the project directory.*
3. Clone ``ckan`` and checkout the required version.
4. Clone ``ckanpi``.
5. Fork and clone the following.

    - ``ckanext-scheming``
    - ``ckanext-fluent``
    - ``ckanext-repeating``
    - ``ckanext-autodoc``

6. Fork, clone and checkout the required version of ``ckanext-wet-boew``.
7. Setup CKAN and the extensions.

    ```
        cd ckan
        pip install -r requirements.txt
        python setup.py develop
        cd ..

        cd ckanapi
        pip install -r requirements.txt
        python setup.py develop
        cd ..

        cd ckanext-wet-boew
        pip install -r requirements.txt
        python setup.py develop
        cd ..

        cd ckanext-scheming
        python setup.py develop
        cd ..

        cd ckanext-fluent
        python setup.py develop
        cd ..

        cd ckanext-repeating
        python setup.py develop
        cd ..

        cd ckanext-autodoc
        python setup.py develop
        cd ..

        cd ckanext-stcndm
        pip install -r requirements.txt
        python setup.py develop
        cd ..
    ```

8. Install WET Resources. *Change `PROJECT DIRECTORY` to your working directory.*

    ```
        mkdir -p wet-boew/wet-boew
        mdkir wet-boew/theme-gc-intranet
        curl -L https://github.com/wet-boew/wet-boew-cdn/archive/v4.0.18.tar.gz | tar -zx --strip-components 1 --directory=PROJECT DIRECTORY/wet-boew/wet-boew
        curl -L https://github.com/wet-boew/themes-cdn/archive/v4.0.18-theme-gc-intranet.tar.gz | tar -zx --strip-components 1 --directory=PROJECT DIRECTORY/wet-boew/theme-gc-intranet
    ```

9. Create a CKAN database.

    ```
        sudo -u postgres createuser -S -D -R -P ckan_default
        sudo -u postgres createdb -O ckan_default stcndm_ckan -E utf-8
    ```

10. Create a new Solr collection. *Change `PROJECT DIRECTORY` to your working directory.*

    ```
        sudo su - solr -c "/opt/solr/bin/solr create -c stcndm -n data_driven_schema_configs"
        sudo -u solr ln -f -s `PROJECT DIRECTORY`/ckanext-stcndm/conf/solr/*.txt /var/solr/data/stcndm/conf
        sudo -u solr ln -f -s `PROJECT DIRECTORY`/ckanext-stcndm/conf/solr/solrconfig-dev.xml /var/solr/data/stcndm/conf/solrconfig.xml
        sudo -u solr ln -f -s `PROJECT DIRECTORY`/ckanext-stcndm/conf/solr/schema-dev.xml /var/solr/data/stcndm/conf/schema.xml
    ```

11. Create and setup CKAN config file. *Change `PROJECT DIRECTORY` to your working directory.*

    ```
        paster make-config ckan development.ini
        ln -s ckan/who.ini who.ini
        sudo mkdir -p /etc/ckan/stcndm
        sudo ln -s `PROJECT DIRECTORY`/*.ini /etc/ckan/stcndm/
    ```

12. Modify the development.ini file and update the following values. *Change `PROJECT DIRECTORY` and `PASSWORD`*

    ```
        sqlalchemy.url = postgresql://ckan_default:`PASSWORD`@localhost/stcndm_ckan
        solr_url = http://localhost:8983/solr/stcndm
        ckan.site_id = stcndm
        ckan.plugins = stats text_view image_view recline_view stcndm stcndm_report_generator repeating scheming_datasets fluent wet_boew_theme_gc_intranet autodoc
        ckan.storage_path = /var/lib/ckan
        extra_public_paths = `PROJECT DIRECTORY`/wet-boew
        wet_boew.jquery.offline = true
        ckan.gravatar_show = false
    ```

13. Initialize the Database.

    ```
        paster --plugin=ckan db init -c /etc/ckan/stcndm/development.ini
        ckanapi -c /etc/ckan/stcndm/development.ini action organization_create name=statcan title="Statistics Canada"
    ```

14. Launch CKAN.

    ```
        paster serve /etc/ckan/stcndm/development.ini
    ```