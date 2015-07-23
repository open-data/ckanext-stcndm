__author__ = 'marc'

import sys
import json

lines = json.load(sys.stdin)
out = []
for line in lines:
    line_out = {'owner_org': 'statcan', 'private': False, 'type': 'subject'}

    if 'tmtaxdisp_en_tmtxtm' in line:
        if line['tmtaxdisp_en_tmtxtm'][0] == 'a_to_z':
            line_out['subject_display_code'] = '1'
        elif line['tmtaxdisp_en_tmtxtm'][0] == 'taxonomy':
            line_out['subject_display_code'] = '2'
        elif line['tmtaxdisp_en_tmtxtm'][0] == 'both':
            line_out['subject_display_code'] = '3'
        elif line['tmtaxdisp_en_tmtxtm'][0] == 'hide':
            line_out['subject_display_code'] = '4'

    temp = {}
    if 'tmtaxsubj_en_tmtxtm' in line:
        temp['en'] = line['tmtaxsubj_en_tmtxtm'][0]
    if 'tmtaxsubj_fr_tmtxtm' in line:
        temp['fr'] = line['tmtaxsubj_fr_tmtxtm'][0]
    if temp:
        line_out['title'] = temp

    if 'tmtaxsubjcode_bi_tmtxtm' in line:
        line_out['subject_code'] = line['tmtaxsubjcode_bi_tmtxtm'][0]
        line_out['name'] = 'subject-{0}'.format(('000000'+line['tmtaxsubjcode_bi_tmtxtm'][0])[-6:])

    if 'tmtaxadminnotes_bi_tmtxts' in line:
        line_out['notes'] = {
            'en': line['tmtaxadminnotes_bi_tmtxts'][0],
            'fr': line['tmtaxadminnotes_bi_tmtxts'][0]
        }

    if 'tmtaxsubjoldcode_bi_tmtxtm' in line:
        line_out['subjectold_code'] = map(unicode.strip, line['tmtaxsubjoldcode_bi_tmtxtm'][0].split(';'))

    temp = {}
    if 'tmtaxatozalias_en_tmtxtm' in line:
        temp['en'] = line['tmtaxatozalias_en_tmtxtm'][0]
    if 'tmtaxatozalias_fr_tmtxtm' in line:
        temp['fr'] = line['tmtaxatozalias_fr_tmtxtm'][0]
    if temp:
        line_out['a_to_z_alias'] = temp

    out.append(line_out)
print json.dumps(out, indent=2)
