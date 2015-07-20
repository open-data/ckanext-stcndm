__author__ = 'marc'

import sys
import json

lookup = {
    'extras_archived_bi_strs': 'archived',
    'extras_conttype_en_txtm': 'content_type',
    'extras_dispandtrack_bi_txtm': 'tracking',
    'extras_display_en_txtm': 'display',
    'extras_format_en_txtm': 'format',
    'extras_freq_en_txtm': 'frequency',
    'extras_geolevel_en_txtm': 'geolevel',
    'extras_producttype_en_strs': 'product_type',
    'extras_statusf_en_strs': 'status',
    'extras_tmregorg_bi_tmtxtm': 'bogon',
    'extras_tmtaxdisp_en_tmtxtm': 'subject_display'
}
lines = json.load(sys.stdin)
out = []

for line in lines:
    if line['tmdroplfld_bi_tmtxtm'][0] in ('extras_archived_bi_strs',
                                           'extras_tmtaxdisp_en_tmtxtm',
                                           'extras_tmregorg_bi_tmtxtm',
                                           'extras_dispandtrack_bi_txtm',
                                           'extras_producttype_en_strs',
                                           'extras_display_en_txtm',
                                           'extras_geolevel_en_txtm',
                                           'extras_format_en_txtm'):
        continue

    line_out = {'owner_org': 'statcan', 'type': 'codeset'}

    if line['tmdroplfld_bi_tmtxtm'][0] == 'extras_geolevel_en_txtm':
        english_value, french_value = map(unicode.strip, (line['tmdroplopt_bi_tmtxtm'][0]).split('|'))
        line_out['codeset_type'] = lookup[line['tmdroplfld_bi_tmtxtm'][0]]
        line_out['codeset_value'] = ''
        line_out['title'] = {
            'en': english_value,
            'fr': french_value
        }
    else:
        english_value, french_value, code_value, bogon = map(unicode.strip,
                                                             (line['tmdroplopt_bi_tmtxtm'][0] + '|||').split('|', 3))
        if not code_value:
            print u'missing code value for {0} {1}'.format(line['tmdroplfld_bi_tmtxtm'][0], line['tmdroplopt_bi_tmtxtm'])
            continue
        else:
            line_out['codeset_type'] = lookup[line['tmdroplfld_bi_tmtxtm'][0]]
            line_out['codeset_value'] = code_value
            line_out['title'] = {
                'en': english_value,
                'fr': french_value
            }

    out.append(line_out)

print json.dumps(out, indent=2)
