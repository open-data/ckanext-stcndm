import json
import ckanapi

import ConfigParser

parser = ConfigParser.SafeConfigParser()
parser.read('ckanparameters.config')
API_KEY = parser.get('ckan', 'api_key')
BASE_URL = parser.get('ckan', 'base_url')

ckan = ckanapi.RemoteCKAN(BASE_URL,
    apikey=API_KEY,
    user_agent="add_users/{version}".format(version=1.0))

with open("qa_user_list.json") as json_file:
    json_data = json.load(json_file)

for user in json_data:
    try:
        query_results = ckan.action.user_create(**user)
    except Exception as e:
        print user['name'], str(e)

