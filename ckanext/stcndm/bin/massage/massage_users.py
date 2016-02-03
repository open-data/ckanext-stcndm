import json
import ckanapi
import ConfigParser

__author__ = 'marc'

skip_users = [
    'default',
    'logged_in',
    'visitor'
]

api_keys = {
    'tabledesigner': '5a8c1a0a-0162-11e5-afed-005056a62458',
    'releaseagent': 'eaf7927f-1055-4b1d-972b-d029d5f2b18f',
    'dailyagent': 'a9752182-86ea-4030-ae9f-498df10841c9',
    'pubsagent': 'b2711cb6-c119-4ec1-9889-4e187d417018',
    'cubeagent': '86595157-99b9-468d-835b-bf0ba6697f4b'
}

parser = ConfigParser.SafeConfigParser()
parser.read("./ckanparameters.config")

API_KEY = parser.get("ckanqa", "api_key")
BASE_URL = parser.get("ckanqa", "base_url")

rc = ckanapi.RemoteCKAN(BASE_URL, apikey=API_KEY)
query_results = rc.action.user_list(include_password_hash=True)
for user in query_results:
    name = user.get('name')
    if name in skip_users:
        continue
    if name in api_keys:
        user['apikey'] = api_keys[name]
    print json.dumps(user)
