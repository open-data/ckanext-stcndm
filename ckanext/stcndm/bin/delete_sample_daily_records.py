import ckanapi
import ckan
import ConfigParser

parser = ConfigParser.SafeConfigParser()
parser.read("./ckanparameters.config")

API_KEY = parser.get("ckandev", "api_key")
BASE_URL = parser.get("ckandev", "base_url")


def main():
    rc = ckanapi.RemoteCKAN(BASE_URL,
                            apikey=API_KEY)

    for i in range(0, 28):

        pid = u"daily-002400011{id}".format(id=str(i).zfill(4))  # 00240001 is the prefix to all daily records

        try:
            rc.action.package_delete(id=pid.lower())
            print "deleted ", pid
        except Exception as e:
            print '{name}: {error}'.format(name=pid, error=e)

if __name__ == "__main__":
    main()
