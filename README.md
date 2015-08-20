# stcndm example extension

Requirements:
* ckan 2.3
* ckanext-scheming
* ckanext-fluent
* ckanext-repeating (if you need repeating free-form fields)
* ckanext-wet-boew and a copy of the WET production files

required settings in developent.ini:
```ini
ckan.plugins =
    text_view recline_grid_view recline_graph_view
    stcndm scheming_datasets fluent wet_theme

scheming.dataset_schemas =
    ckanext.stcndm:schemas/codeset.yaml
    ckanext.stcndm:schemas/conf_service.yaml
    ckanext.stcndm:schemas/corrections.yaml
    ckanext.stcndm:schemas/cube.yaml
    ckanext.stcndm:schemas/daily.yaml
    ckanext.stcndm:schemas/indicator.yaml
    ckanext.stcndm:schemas/issue.yaml
    ckanext.stcndm:schemas/publication.yaml
    ckanext.stcndm:schemas/pumf.yaml
    ckanext.stcndm:schemas/subject.yaml
    ckanext.stcndm:schemas/view.yaml
    ckanext.stcndm:schemas/survey.yaml


scheming.presets =
    ckanext.scheming:presets.json
    ckanext.fluent:presets.json
    ckanext.stcndm:schemas/presets.yaml
    
wet_theme.url = http://localhost:5000/theme-intranet

wet_theme.geo_map_type = static
```

Templates have not been customized, you can find the editing forms
for the primary and format types at:
* /primary/new
* /format/new


## Installation

  1. Create empty Solr and PostgreSQL instances as per the normal CKAN installation process.
  2. On GitHub, fork your own copy of https://github.com/open-data/ckanext-stcndm.git
  3. In your project directory, clone the following GitHub projects:
    *  https://github.com/ckan/ckan.git
    *  https://github.com/ckan/ckanapi.git
    *  https://github.com/open-data/ckanext-scheming.git
    *  https://github.com/open-data/ckanext-fluent.git
    *  https://github.com/open-data/ckanext-repeating
    *  https://github.com/open-data/ckanext-wet-boew.git
    *  https://github.com/<your fork&gt;/ckanext-stcndm.git
  4. Create and activate a virtual environment for your project:
  ```
   virtualenv --no-site-packages stcndm
   source stcndm/bin/activate
  ```
  5. Use version 2.3 of CKAN
  ```
    cd ckan
    git checkout release-v2.3.1
    cd ..
  ```
  
  6. Use the wet4-scheming branch of the Open Data CKAN WET extension
    ```
    cd ckanext-wet-boew
    git checkout wet4-scheming
    cd ..
  ```
  
  7. Install the requirements for CKAN. Please note, that you may encounter problems installing the 'pbr' package.
     In this case, just install pdr manually from pypi.
  ```
    pip install pbr
  ```     
  8. Install the requirements and other projects.
  
  ```
    
    cd ckan
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

    cd ckanext-stcndm
    pip install -r requirements.txt
    python setup.py develop
    cd ..
  ``` 
  9. Install the libgeos library required by ckanext-wet-beow (`brew install geos` on OS X or `apt-get install libgeos-dev` on Debian/Ubuntu)
  10. Create the .ini file as per the normal CKAN installation instructions and modify as noted above.
  
  11. Configure the WET extension for use as per https://github.com/open-data/ckanext-wet-boew/tree/wet4-scheming
      Download the WET intranet theme production ZIP file from 
      http://wet-boew.github.io/wet-boew/docs/versions/dwnld-en.html and extract it into the 'ckanext/stcndm/public'
      directory in the ckanext-stcndm project. Rename the extracted folder to theme-intranet
      You may need to copy minified versions of jquery-1.11.1.min.js and jquery-2.1.1.min.js to the theme-intranet
      directory.
  
  12. Create an organization with the URL statcan and the name Statistics Canada

    
