import configparser
from database import postgresql

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

db.query("""CREATE TABLE IF NOT EXISTS "current"(
            "startTime" TIMESTAMP WITH TIME ZONE NOT NULL,
            "dnsId" TEXT NOT NULL,
            "domainId" TEXT NOT NULL,
            "cellId" TEXT NOT NULL,
            "deviceId" TEXT NOT NULL,
            "imei" TEXT NOT NULL,
            "ipv4" TEXT NOT NULL,
            "ipv6" TEXT NOT NULL,
            "sliceId" TEXT NOT NULL,
            "fqdn" TEXT NOT NULL);""")




db.query("""CREATE TABLE IF NOT EXISTS "history"(
            "startTime" TIMESTAMP WITH TIME ZONE NOT NULL,
            "endTime" TIMESTAMP WITH TIME ZONE,
            "previous" TEXT NOT NULL,
            "next" TEXT,
            "dnsId" TEXT NOT NULL,
            "domainId" TEXT NOT NULL,
            "cellId" TEXT NOT NULL,
            "deviceId" TEXT NOT NULL,
            "imei" TEXT NOT NULL,
            "ipv4" TEXT NOT NULL,
            "ipv6" TEXT NOT NULL,
            "sliceId" TEXT NOT NULL,
            "fqdn" TEXT NOT NULL);""")




db.query(""" CREATE TABLE IF NOT EXISTS "callFlow"(
            "datetime" TIMESTAMP WITH TIME ZONE NOT NULL,
            "type" TEXT NOT NULL,
            "payload" TEXT NOT NULL);""")



db.query("""CREATE TABLE IF NOT EXISTS "systemLog"(
            "datetime" TIMESTAMP WITH TIME ZONE NOT NULL,
            "dnsEnvInfo" TEXT NOT NULL,
            "dnsId" TEXT NOT NULL,
            "cpuUsage" FLOAT NOT NULL,
            "memoryUsage" FLOAT NOT NULL,
            "diskUsage" FLOAT NOT NULL);""")
