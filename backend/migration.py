import os, configparser, psycopg2

cfgpath = os.path.abspath('.') + "/config.ini"

config = configparser.ConfigParser()
config.read(cfgpath)

def create_current():
    pg = psycopg2.connect(database = config['database']['database'],host = config['database']['host'], user = config['database']['user'], password = config['database']['password'], port = config['database']['port'])
    pg_cur = pg.cursor()

    pg_cur.execute(""" CREATE TABLE IF NOT EXISTS current(
                        "Start_time" TIMESTAMP WITH TIME ZONE NOT NULL,
                        "DNS_ID" TEXT NOT NULL,
                        "Domain_ID" TEXT NOT NULL,
                        "Cell_ID" TEXT NOT NULL,
                        "Device_ID" TEXT NOT NULL,
                        "IMEI" TEXT NOT NULL,
                        "IPv4" TEXT NOT NULL,
                        "IPv6" TEXT NOT NULL,
                        "FQDN" TEXT NOT NULL);""")

    pg.commit()
    pg.close()
    print("Success create current")

def create_history():
    pg = psycopg2.connect(database = config['database']['database'],host = config['database']['host'], user = config['database']['user'], password = config['database']['password'], port = config['database']['port'])
    pg_cur = pg.cursor()

    pg_cur.execute(""" CREATE TABLE IF NOT EXISTS history(
                        "Start_time" TIMESTAMP WITH TIME ZONE NOT NULL,
                        "End_time" TIMESTAMP WITH TIME ZONE,
                        "Previous" TEXT NOT NULL,
                        "Next" TEXT,
                        "DNS_ID" TEXT NOT NULL,
                        "Domain_ID" TEXT NOT NULL,
                        "Cell_ID" TEXT NOT NULL,
                        "Device_ID" TEXT NOT NULL,
                        "IMEI" TEXT NOT NULL,
                        "IPv4" TEXT NOT NULL,
                        "IPv6" TEXT NOT NULL,
                        "FQDN" TEXT NOT NULL);""")

    pg.commit()
    pg.close()
    print("Success create history")

def create_call_flow():
    pg = psycopg2.connect(database = config['database']['database'],host = config['database']['host'], user = config['database']['user'], password = config['database']['password'], port = config['database']['port'])
    pg_cur = pg.cursor()

    pg_cur.execute(""" CREATE TABLE IF NOT EXISTS call_flow(
                        "Datetime" TIMESTAMP WITH TIME ZONE NOT NULL,
                        "Type" TEXT NOT NULL,
                        "Payload" TEXT NOT NULL);""")

    pg.commit()
    pg.close()
    print("Success create call_flow")

def create_system_log():
    pg = psycopg2.connect(database = config['database']['database'],host = config['database']['host'], user = config['database']['user'], password = config['database']['password'], port = config['database']['port'])
    pg_cur = pg.cursor()

    pg_cur.execute(""" CREATE TABLE IF NOT EXISTS system_log(
                        "Datetime" TIMESTAMP WITH TIME ZONE NOT NULL,
                        "DNS_env_info" TEXT NOT NULL,
                        "DNS_ID" TEXT NOT NULL,
                        "CPU_Usage" FLOAT NOT NULL,
                        "Memory_Usage" FLOAT NOT NULL,
                        "Disk_Usage" FLOAT NOT NULL);""")

    pg.commit()
    pg.close()
    print("Success create system_log")

create_current()
create_history()
create_call_flow()
create_system_log()

