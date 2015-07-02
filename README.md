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
    ckanext.stcndm:schemas/primary.yaml
    ckanext.stcndm:schemas/format.yaml

scheming.presets =
    ckanext.scheming:presets.json
    ckanext.fluent:presets.json
    ckanext.stcndm:schemas/presets.yaml
```

Templates have not been customized, you can find the editing forms
for the primary and format types at:
* /primary/new
* /format/new
