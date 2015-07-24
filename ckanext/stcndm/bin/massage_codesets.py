__author__ = 'marc'

import sys
import json
from ckan.plugins.toolkit import missing, _

lookup = {
    'extras_conttype_en_txtm': u'content_type',
    'extras_freq_en_txtm': u'frequency',
    'extras_statusf_en_strs': u'status',
    # geolevel is still a codeset but is treated separately
    # 'extras_geolevel_en_txtm': 'geolevel',
    # the following fields have become presets
    # 'extras_archived_bi_strs': 'archived',
    # 'extras_dispandtrack_bi_txtm': 'tracking',
    # 'extras_display_en_txtm': 'display',
    # 'extras_format_en_txtm': 'format',
    # 'extras_producttype_en_strs': 'product_type',
    # 'extras_tmregorg_bi_tmtxtm': 'bogon',
    # 'extras_tmtaxdisp_en_tmtxtm': 'subject_display'
}
lines = json.load(sys.stdin)
out = []

for line in lines:
    old_content_type = line['tmdroplfld_bi_tmtxtm'][0]
    if old_content_type in ('extras_archived_bi_strs',
                            'extras_tmtaxdisp_en_tmtxtm',
                            'extras_tmregorg_bi_tmtxtm',
                            'extras_dispandtrack_bi_txtm',
                            'extras_producttype_en_strs',
                            'extras_display_en_txtm',
                            'extras_geolevel_en_txtm',
                            'extras_format_en_txtm',
                            'extras_display_bi_txtm'):
        continue  # skip the tmshorlist that are handled separately

    line_out = {u'owner_org': u'statcan',
                u'private': False,
                u'type': u'codeset'}

    data = line['tmdroplopt_bi_tmtxtm'][0]
    english_value, french_value, code_value, bogon = map(unicode.strip, (data + u'|||').split(u'|', 3))
    if not code_value:
        sys.stderr.write('missing code value for {0} {1}\n'.format(old_content_type, data))
        continue
    else:
        codeset_type = lookup[line['tmdroplfld_bi_tmtxtm'][0]]
        line_out['name'] = u'codeset-{0}-{1}'.format(codeset_type, code_value)
        print
        line_out['codeset_type'] = lookup[old_content_type]
#        line_out['codeset_value'] = ('00{0}'.format(code_value))[-2:]
        line_out['codeset_value'] = code_value
        line_out['title'] = {
            u'en': english_value,
            u'fr': french_value
        }

    out.append(line_out)

print json.dumps(out, indent=2)
