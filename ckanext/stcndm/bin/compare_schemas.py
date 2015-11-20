import yaml
import os
import sys
import xmltodict

# the purpose of this script is to compare the fields in the .yaml
# schema files to the solr schema file to detect inconsistencies

with open('../../../conf/solr/schema-dev.xml') as fd:
    solrMap = xmltodict.parse(fd.read())
solr_dict = {}
for field in solrMap['schema']['fields']['field']:
    solr_dict[field['@name']] = {
        'indexed': field.get('@indexed'),
        'stored': field.get('@stored'),
        'type': field.get('@type'),
        'multiValued': field.get('@multiValued')
    }

presets_dict = {}
f = open('../schemas/presets.yaml')
presetMap = yaml.safe_load(f)
f.close()
for preset in presetMap[u'presets']:
    presets_dict[preset['preset_name']] = {
        'schema_field_type': preset.get('values', {}).get('schema_field_type'),
        'schema_multivalued':
            preset.get('values', {}).get('schema_multivalued'),
        'schema_extras': preset.get('values', {}).get('schema_extras')
    }


def schema_lookup(find_field, dataset):
    a_preset = presets_dict.get(dataset.get('preset', ''), {})
    return dataset.get(find_field, a_preset.get(find_field))


def compare(a_field_name, field_dict):
    if a_field_name not in solr_dict:
        sys.stderr.write(
            '{a_file}: {dataset_field} missing from solr\n'.format(
                a_file=a_file,
                dataset_field=a_field_name
            )
        )
    else:
        ckan_multi_valued = schema_lookup('schema_multivalued', field_dict)
        solr_multi_valued = solr_dict[a_field_name].get('multiValued', '')
        if ckan_multi_valued is None or solr_multi_valued is None:
            sys.stderr.write(
                '{a_file}: {dataset_field} unable to determine multiValue\n'
                .format(
                    a_file=a_file,
                    dataset_field=a_field_name
                )
            )
        elif (ckan_multi_valued and solr_multi_valued.lower() != 'true') or (
                not ckan_multi_valued and solr_multi_valued.lower() != 'false'):
                sys.stderr.write(
                    '{a_file}: {dataset_field} multiValue mismatch\n'.format(
                        a_file=a_file,
                        dataset_field=a_field_name
                    )
                )


for a_file in os.listdir('../schemas/'):
    if a_file.endswith('.yaml'):
        f = open('../schemas/'+a_file)
        yamlMap = yaml.safe_load(f)
        f.close()
        dataset_fields = yamlMap.get('dataset_fields', [])
        for dataset_field in dataset_fields:
            field_name = dataset_field.get('field_name')
            if field_name:
                if field_name == 'owner_org':
                    continue
                field_type = schema_lookup('schema_field_type', dataset_field)
                if field_type is None:
                    sys.stderr.write(
                        '{a_file}: {dataset_field} '
                        'unable to determine field type\n'
                        .format(
                            a_file=a_file,
                            dataset_field=field_name
                        )
                    )
                    continue
                elif field_type == 'fluent':
                    compare(field_name+'_en', dataset_field)
                    compare(field_name+'_fr', dataset_field)
                elif field_type == 'code':
                    compare(field_name+'_desc_en', dataset_field)
                    compare(field_name+'_desc_fr', dataset_field)
                else:
                    compare(field_name, dataset_field)
