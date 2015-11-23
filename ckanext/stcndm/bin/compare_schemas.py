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


def compare(a_ckan_field_name, a_ckan_field_dict):
    if a_ckan_field_name not in solr_dict:
        sys.stderr.write(
            '{a_file}: {dataset_field} missing from solr\n'.format(
                a_file=a_file,
                dataset_field=a_ckan_field_name
            )
        )
    else:
        ckan_multi_valued = schema_lookup(
            'schema_multivalued',
            a_ckan_field_dict)
        solr_multi_valued = solr_dict[a_ckan_field_name].get('multiValued', '')
        if ckan_multi_valued is None or solr_multi_valued is None:
            sys.stderr.write(
                '{a_file}: {dataset_field} unable to determine multiValue\n'
                .format(
                    a_file=a_file,
                    dataset_field=a_ckan_field_name
                )
            )
        elif (ckan_multi_valued and solr_multi_valued.lower() != 'true') or (
                not ckan_multi_valued and solr_multi_valued.lower() != 'false'):
                sys.stderr.write(
                    '{a_file}: {dataset_field} multiValue mismatch\n'.format(
                        a_file=a_file,
                        dataset_field=a_ckan_field_name
                    )
                )


for a_file in os.listdir('../schemas/'):
    if a_file.endswith('.yaml'):
        f = open('../schemas/'+a_file)
        yamlMap = yaml.safe_load(f)
        f.close()
        ckan_fields = yamlMap.get('dataset_fields', [])
        for ckan_field_dict in ckan_fields:
            ckan_field_name = ckan_field_dict.get('field_name')
            if ckan_field_name:
                if ckan_field_name == 'owner_org':
                    continue
                field_type = schema_lookup('schema_field_type', ckan_field_dict)
                if field_type is None:
                    sys.stderr.write(
                        '{a_file}: {dataset_field} '
                        'unable to determine field type\n'
                        .format(
                            a_file=a_file,
                            dataset_field=ckan_field_name
                        )
                    )
                    continue
                elif field_type == 'fluent':
                    compare(ckan_field_name + '_en', ckan_field_dict)
                    compare(ckan_field_name + '_fr', ckan_field_dict)
                elif field_type == 'code':
                    compare(ckan_field_name + '_desc_en', ckan_field_dict)
                    compare(ckan_field_name + '_desc_fr', ckan_field_dict)
                elif field_type == 'date':
                    compare(ckan_field_name, ckan_field_dict)
                    if not solr_dict.get(ckan_field_name, {}).get('type', '') \
                       == 'date':
                        sys.stderr.write(
                            '{a_file}: {dataset_field} type mismatch\n'.format(
                                a_file=a_file,
                                dataset_field=ckan_field_name
                            )
                        )
                else:
                    compare(ckan_field_name, ckan_field_dict)
