# Statistics Canada's New New Dissemination CKAN Extension

## Requirements

* Solr 5.2.1
* PostgreSQL
* ckan v2.4-ndm
* ckanext-scheming
* ckanext-fluent
* ckanext-repeating
* ckanext-autodoc
* ckanext-history
* ckanext-wet-boew and a copy of the WET production files

## Installation

  1. Install the following package using your OS package manager

  ```
  python-dev postgresql libpq-dev python-pip python-virtualenv git-core libgeos-dev
  ```

  2. In your home directory, create a folder for ndm

  ```
  mkdir stcndm
  cd stcndm
  ```

  3. Create a python virtual environment

  ```
  mkdir venv
  sudo mkdir /usr/lib/ckan
  virtualenv --no-site-packages venv
  sudo ln -s ~/stcndm/venv /usr/lib/ckan/stcndm
  . /usr/lib/ckan/stcndm/bin/activate
  ```

  4. Clone CKAN and ckanapi and checkout version 2.4-ndm of ckan

    * https://github.com/open-data/ckan.git
    * https://github.com/ckan/ckanapi.git

  ```
  git clone https://github.com/open-data/ckan.git
  git clone https://github.com/ckan/ckanapi.git
  cd ckan
  git checkout release-v2.4-ndm
  cd ..
  ```

  5. Fork the following repos and clone them
    *  https://github.com/open-data/ckanext-scheming.git
    *  https://github.com/open-data/ckanext-fluent.git
    *  https://github.com/open-data/ckanext-repeating.git
    *  https://github.com/open-data/ckanext-wet-boew.git
    *  https://github.com/open-data/ckanext-stcndm.git
    *  https://github.com/open-data/ckanext-autodoc.git
    *  https://github.com/open-data/ckanext-history.git

  ```
  git clone https://github.com/[Your_Fork]/ckanext-scheming.git
  git clone https://github.com/[Your_Fork]/ckanext-fluent.git
  git clone https://github.com/[Your_Fork]/ckanext-repeating.git
  git clone https://github.com/[Your_Fork]/ckanext-wet-boew.git
  git clone https://github.com/[Your_Fork]/ckanext-stcndm.git
  git clone https://github.com/[Your_Fork]/ckanext-autodoc.git
  git clone https://github.com/[Your_Fork]/ckanext-history.git
  ```

  6. Use the wet4-scheming branch of the Open Data CKAN WET extension.

  ```
  cd ckanext-wet-boew
  git checkout wet4-scheming
  cd ..
  ```

  7. Install the requirements for ckan and each extension.

  ```
  cd ckan
  pip install -r requirements.txt
  python setup.py develop
  cd ..

  cd ckanapi
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

  cd ckanext-history
  python setup.py develop
  cd ..

  cd ckanext-stcndm
  pip install -r requirements.txt
  python setup.py develop
  cd ..
  ```

  8. Create a new PostgreSQL databases

  ```
  sudo -u postgres createuser -S -D -R -P ckan_default
  sudo -u postgres createuser -S -D -R -P -l datastore_default
  sudo -u postgres createdb -O ckan_default stcndm_ckan -E utf-8
  sudo -u postgres createdb -O ckan_default stcndm_ckan_datastore -E utf-8
  ```

  9. Create a new Solr collection

  ```
  sudo su - solr -c "/opt/solr/bin/solr create -c stcndm -n data_driven_schema_configs"
  sudo -u solr ln -f -s ~/stcndm/ckanext-stcndm/conf/solr/*.txt /var/solr/data/stcndm/conf
  sudo -u solr ln -f -s ~/stcndm/ckanext-stcndm/conf/solr/solrconfig-dev.xml /var/solr/data/stcndm/conf/solrconfig.xml
  sudo -u solr ln -f -s ~/stcndm/ckanext-stcndm/conf/solr/schema-dev.xml /var/solr/data/stcndm/conf/schema.xml
  ```

  10. Create a CKAN config file and link the who.ini

  ```
  paster make-config ckan development.ini
  ln -s ~/stcndm/ckan/who.ini who.ini
  sudo mkdir -p /etc/ckan/stcndm
  sudo ln -s ~/stcndm/*.ini /etc/ckan/stcndm/
  ```

  11. Modify the development.ini file with the following values:

    * `sqlalchemy.url = postgresql://ckan_default:pass@localhost/stcndm_ckan`
    * `ckan.datastore.write_url = postgresql://ckan_default:pass@localhost/stcndm_ckan_datastore`
    * `ckan.datastore.read_url = postgresql://datastore_ckan:pass@localhost/stcndm_ckan_datastore`
    * `solr_url = http://localhost:8983/solr/stcndm`
    * `ckan.site_id = stcndm`
    * `ckan.plugins = datastore stats text_view image_view recline_view
    stcndm stcndm_report_generator repeating scheming_datasets fluent
    wet_boew_theme_gc_intranet history autodoc`

  12. Initialize the database

  ```
  paster --plugin=ckan db init -c development.ini
  paster --plugin=ckan datastore set-permissions -c development.ini | sudo -u postgres psql
  ```

  13. Configure the WET extension for use as per https://github.com/open-data/ckanext-wet-boew/tree/wet4-scheming

  14. Create the Statcan organization

  ```
  ckanapi action organization_create name=statcan title="Statistics Canada"
  ```

  15. Launch CKAN

  ```
  paster serve ~/stcndm/development.ini
  ```

  ### Importing Authors

  To import authors, first ensure you have a user and get yout api key from you user profile page. The run the following command:

  ```
  python ckanext-stcndm/bin/insert_authors.py http://localhost:5000 [authors.csv] --api-key=[key]
  ```
