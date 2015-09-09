import json
import ckanapi
import ConfigParser

parser = ConfigParser.SafeConfigParser()
parser.read('ckanparameters.config')
API_KEY = parser.get('ckan', 'api_key')
BASE_URL = parser.get('ckan', 'base_url')


ckan = ckanapi.RemoteCKAN(BASE_URL,
    apikey=API_KEY,
    user_agent="get_users/{version}".format(version=1.0))

query_results = ckan.action.user_list()
users = list()
for user in query_results:
    user['password'] = "Password1"
    del user['number_of_edits']
    del user['number_administered_packages']
    users.append(user)

print json.dumps(users)
