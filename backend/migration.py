import os
import configparser
import psycopg2

cfgpath = os.path.abspath('.') + "/config.ini"

config = configparser.ConfigParser()
config.read(cfgpath)


def create_current():
    pg = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                          user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
    pg_cur = pg.cursor()

    pg_cur.execute(""" CREATE TABLE IF NOT EXISTS "current"(
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

    pg.commit()
    pg.close()
    print("Success create current")


def create_history():
    pg = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                          user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
    pg_cur = pg.cursor()

    pg_cur.execute(""" CREATE TABLE IF NOT EXISTS "history"(
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

    pg.commit()
    pg.close()
    print("Success create history")


def create_call_flow():
    pg = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                          user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
    pg_cur = pg.cursor()

    pg_cur.execute(""" CREATE TABLE IF NOT EXISTS "callFlow"(
                        "datetime" TIMESTAMP WITH TIME ZONE NOT NULL,
                        "type" TEXT NOT NULL,
                        "payload" TEXT NOT NULL);""")

    pg.commit()
    pg.close()
    print("Success create call_flow")


def create_system_log():
    pg = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                          user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
    pg_cur = pg.cursor()

    pg_cur.execute(""" CREATE TABLE IF NOT EXISTS "systemLog"(
                        "datetime" TIMESTAMP WITH TIME ZONE NOT NULL,
                        "dnsEnvInfo" TEXT NOT NULL,
                        "dnsId" TEXT NOT NULL,
                        "cpuUsage" FLOAT NOT NULL,
                        "memoryUsage" FLOAT NOT NULL,
                        "diskUsage" FLOAT NOT NULL);""")

    pg.commit()
    pg.close()
    print("Success create system_log")


create_current()
create_history()
create_call_flow()
create_system_log()
