# stcndm example extension

Requirements:
* ckan 2.3
* ckanext-scheming
* ckanext-fluent
* ckanext-repeating (if you need repeating free-form fields)

required settings in developent.ini:
```ini
ckan.plugins =
    text_view recline_grid_view recline_graph_view
    stcndm scheming_datasets fluent

scheming.dataset_schemas =
    ckanext.stcndm:schemas/cube.yaml


scheming.presets =
    ckanext.scheming:presets.json
    ckanext.fluent:presets.json
    ckanext.stcndm:schemas/presets.yaml
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
    *  https://github.com/<your fork>/ckanext-stcndm.git
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
  6. Install the requirements for CKAN. Please note, that you may encounter problems installing the 'pbr' package.
     In this case, just install pdr manually from pypi.
  ```
    pip install pbr
  ```     
  7. Install the requirements and other projects.
  
  ```
    
    cd ckan
    python setup.py develop
    cd ..
    
    cd ckanapi
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
    
    pip install -r ckanext-stcndm/requirements.txt
    cd ckanext-stcndm
    python setup.py develop
    cd ..
  ``` 
  8. Create the .ini file as per the normal CKAN installation instructions and modify as noted above.

    