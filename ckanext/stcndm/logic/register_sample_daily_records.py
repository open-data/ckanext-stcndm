
import datetime
import ckanapi
import ckan
import ConfigParser

parser = ConfigParser.SafeConfigParser()
parser.read('./ckanparameters.config')

API_KEY = parser.get('ckan', 'api_key')
BASE_URL = parser.get('ckan', 'base_url')


def get_daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield str(start_date + datetime.timedelta(n))


def main():
    rc = ckanapi.RemoteCKAN(BASE_URL,
                              apikey=API_KEY,
                              user_agent='register_sample_daily_records')

    start_date = datetime.datetime.now()
    end_date = datetime.datetime.now() + datetime.timedelta(weeks=4)

    daterange = get_daterange(start_date, end_date)

    count = 0

    for date in daterange:

        pid = "002400011{id}".format(id=str(count).zfill(4))  # 00240001 is the prefix to all daily records

        pkg_dict = {"productId": pid,
                    "productTitle": {"en": "sample data - {pid}".format(pid=pid),
                                     "fr": "sample data - {pid}".format(pid=pid)},
                    "releaseDate": str(date)[:10],
                    "uniqueId": "daily{pid}".format(pid=pid[-4:]),
                    "lastPublishStatusCode": "08",
                    "childList": "12345"}

        print rc.action.RegisterDaily(**pkg_dict)
        try:
            print rc.action.RegisterDaily(**pkg_dict)

        except ckan.logic.ValidationError:
            print "dataset already registered: {pid}".format(pid=pid)

        count += 1


if __name__ == '__main__':
    main()