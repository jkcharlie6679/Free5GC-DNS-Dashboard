from database import postgresql
import configparser
import datetime

config = configparser.ConfigParser()
config.read("config.ini")

dbConfig = {
    "host": config["database"]["host"],
    "port": config["database"]["port"],
    "user": config["database"]["user"],
    "passwd": config["database"]["passwd"],
    "database": config["database"]["database"],
}

db = postgresql(dbConfig)

dnsFile = config['DNS']['FILE']

timezone8 = datetime.timezone(datetime.timedelta(hours=8))

def timeNow():
    return datetime.datetime.now().replace(microsecond=0).astimezone().isoformat()

def timeToString(time):
    return datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M%z")