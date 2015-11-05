import ckanapi
import ConfigParser

parser = ConfigParser.SafeConfigParser()
parser.read("./ckanparameters.config")

API_KEY = parser.get('ckan', 'api_key')
BASE_URL = parser.get('ckan', 'base_url')

DATASET_TYPES_TO_UPDATE = ['article',
                           'publication',
                           'cube',
                           'view',
                           'indicator',
                           'format']

def main():
    rc = ckanapi.RemoteCKAN(BASE_URL, apikey=API_KEY)

    for dataset_type in DATASET_TYPES_TO_UPDATE:

        # TODO: all cubes and many articles are missing some of these fields in their releases

        q = u'dataset_type:{dataset_type}'.format(dataset_type=dataset_type)

        i = 0
        n = 1

        while i < n:
            query_results = rc.action.package_search(
                q=q,
                rows=1000,
                start=i*1000
            )
            n = query_results['count'] / 1000.0
            i += 1

            for record in query_results['results']:

                release = rc.action.package_search(
                    q='dataset_type:release AND parent_id:{product_id_new}'.format(
                        product_id_new=record['product_id_new']
                    ),
                    rows=1,
                    sort='release_date desc'
                )

                if release['count'] > 0:
                    latest_release = release['results'][0]
                    try:
                        record['last_release_date'] = latest_release['release_date']
                    except KeyError:
                        print '{record}: missing last_release_date'.format(
                            record=record['name']
                        )
                    for field in ['reference_period',
                                  'display_code',
                                  'issue_number']:
                        try:
                            record[field] = latest_release[field]
                        except KeyError:
                            print '{record}: missing {field}'.format(
                                record=record['name'],
                                field=field
                            )

                    rc.action.package_update(**record)

if __name__ == "__main__":
    main()
