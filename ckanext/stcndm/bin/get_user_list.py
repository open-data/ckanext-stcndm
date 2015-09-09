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
    # use the API key for the password if present
    if user['apikey']:
        user['password'] = user['apikey']
    else:
        user['password'] = "pass4{name}!".format(name=user['name'])

    user['number_of_edits'] = 0
    user['number_administered_packages'] = 0
    users.append(user)

print json.dumps(users)
