# Headless UI Test for STCNDM-CKAN #

Functional tests for the CKANEXT-STCNDM.  It does front-end and api based tests against test data.

## Requirements ##

- Selenium
- Phantomjs

## Installation ##

1. Install the following python package using pip

    ```
    pip install selenium
    ```

2. Install the following packages using your OS package manager:for RedHat/CentOS,

    ```
    fontconfig freetype freetype-devel fontconfig-devel libstdc++
    ```

    or for Debian/Ubuntu,

    ```
    build-essential g++ flex bison gperf ruby perl libsqlite3-dev \
    libfontconfig1-dev libicu-dev libfreetype6 libssl-dev \
    libpng-dev libjpeg-dev libx11-dev libxext-dev
    ```

3. Install the phantomjs

    ```
    wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.8-linux-x86_64.tar.bz2
    sudo tar -xjvf phantomjs-1.9.8-linux-x86_64.tar.bz2 -C /usr/local/bin/ phantomjs-1.9.8-linux-x86_64/bin/phantomjs --strip-components 2
    ```

4. Create test database users

    ```
    sudo -u postgres createuser -S -D -R -P ndmuser
    sudo -u postgres createuser -S -D -R -P ndmuser_datastore
    ```

5. Setup the test database

    ```
    sudo -u postgres createdb -O ndmuser stcndm_test -E utf-8
    sudo -u postgres createdb -O ndmuser stcndm_test_datastore -E utf-8
    ```

6. Copy development.ini to test-core.ini and add symbolic link to /etc/ckan/stcndm/. Update URLs.

    ```
    sqlalchemy.url = postgresql://ndmuser:pass@localhost/stcndm_test
    ckan.datastore.write_url = postgresql://ndmuser:pass@localhost/stcndm_test_datastore
    ckan.datastore.read_url = postgresql://ndmuser_datastore:pass@localhost/stcndm_test_datastore
    solr_url = http://127.0.0.1:8983/solr/stcndm_test
    ```

7. Create a solr core:

    ```
    sudo su - solr -c "/opt/solr/bin/solr create -c stcndm_test -n data_driven_schema_configs"
    sudo -u solr ln -f -s ~/stcndm/ckanext-stcndm/conf/solr/*.txt /var/solr/data/stcndm_test/conf
    sudo -u solr ln -f -s ~/stcndm/ckanext-stcndm/conf/solr/solrconfig-dev.xml /var/solr/data/stcndm_test/conf/solrconfig.xml
    sudo -u solr ln -f -s ~/stcndm/ckanext-stcndm/conf/solr/schema-dev.xml /var/solr/data/stcndm_test/conf/schema.xml
    ```

8. To run the tests:

    ```
    source functionaltest_runner.sh
    ```
