import json
import os
import configparser
import datetime
import psycopg2
from flask import Flask, request
from flask_api import status
from flask_cors import cross_origin

app = Flask(__name__)

cfgpath = os.path.abspath('.') + "/config.ini"

config = configparser.ConfigParser()
config.read(cfgpath)

tz_8 = datetime.timezone(datetime.timedelta(hours=8))


@app.route('/resource_usage', methods=['GET'])
@cross_origin()
def resource_usage():
    pg = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                          user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
    pg_cur = pg.cursor()
    return_json = []
    pg_cur.execute(
        """SELECT DISTINCT ON ("DNS_ID") * FROM system_log ORDER BY "DNS_ID", "Datetime" DESC""")
    sql_data = pg_cur.fetchall()
    pg.close()

    for raw in sql_data:
        item_json = {}
        item_json["DNS_ID"] = raw[2]
        item_json["CPU_Usage"] = raw[3]
        item_json["Memory_Usage"] = raw[4]
        item_json["Disk_Usage"] = raw[5]
        return_json.append(item_json)

    return json.dumps(return_json), status.HTTP_200_OK


@app.route('/current', methods=['POST', 'GET', 'DELETE'])
@cross_origin()
def current():
    if request.method == 'POST':
        get_json = request.json
        pg = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                              user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
        pg_cur = pg.cursor()
        return_json = {}
        try:
            pg_cur.execute(
                """SELECT * FROM current WHERE "IMEI" = '{}'""".format(get_json["IMEI"]))
        except KeyError as error:
            pg.close()
            return_json["parameter"] = str(error).replace("'", '')
            return_json["message"] = "Missing " + str(error).replace("'", '')
            return json.dumps(return_json), status.HTTP_400_BAD_REQUEST
        sql_data = pg_cur.fetchall()
        if len(sql_data) == 1:
            try:
                pg_cur.execute("""UPDATE current SET "Start_time" = '{}',
                                                    "DNS_ID" = '{}',
                                                    "Domain_ID" = '{}',
                                                    "Cell_ID" = '{}',
                                                    "Device_ID" = '{}',
                                                    "IMEI" = '{}',
                                                    "IPv4" = '{}',
                                                    "IPv6"= '{}',
                                                    "FQDN" = '{}' WHERE "IMEI" = '{}';"""
                               .format(datetime.datetime.now().replace(microsecond=0).astimezone().isoformat(),
                                       get_json["DNS_ID"],
                                       get_json["Domain_ID"],
                                       get_json["Cell_ID"],
                                       get_json["Device_ID"],
                                       get_json["IMEI"],
                                       get_json["IPv4"],
                                       get_json["IPv6"],
                                       get_json["FQDN"],
                                       get_json["IMEI"]))
                pg.commit()
                pg_cur.execute("""UPDATE history SET "End_time" = '{}', "Next" = '{}' WHERE "Start_time" = '{}';"""
                               .format(datetime.datetime.now().replace(microsecond=0).astimezone().isoformat(),
                                       "Hand off to " + get_json["Cell_ID"],
                                       sql_data[0][0]))
                pg.commit()
                pg_cur.execute("""INSERT INTO history("Start_time", "Previous", "DNS_ID", "Domain_ID", "Cell_ID", "Device_ID", "IMEI", "IPv4", "IPv6", "FQDN")
                                    VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}' ,'{}' ,'{}');"""
                               .format(datetime.datetime.now().replace(microsecond=0).astimezone().isoformat(),
                                       "Hand off from " + sql_data[0][3],
                                       get_json["DNS_ID"],
                                       get_json["Domain_ID"],
                                       get_json["Cell_ID"],
                                       get_json["Device_ID"],
                                       get_json["IMEI"],
                                       get_json["IPv4"],
                                       get_json["IPv6"],
                                       get_json["FQDN"]))
                pg.commit()
            except KeyError as error:
                pg.close()
                return_json["parameter"] = str(error).replace("'", '')
                return_json["message"] = "Missing " + \
                    str(error).replace("'", '')
                return json.dumps(return_json), status.HTTP_400_BAD_REQUEST
            pg.close()
            return_json["message"] = "Update success"
            return json.dumps(return_json), status.HTTP_200_OK
        else:
            try:
                pg_cur.execute("""INSERT INTO current("Start_time", "DNS_ID", "Domain_ID", "Cell_ID", "Device_ID", "IMEI", "IPv4", "IPv6", "FQDN")
                                    VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}' ,'{}' ,'{}');"""
                               .format(datetime.datetime.now().replace(microsecond=0).astimezone().isoformat(),
                                       get_json["DNS_ID"],
                                       get_json["Domain_ID"],
                                       get_json["Cell_ID"],
                                       get_json["Device_ID"],
                                       get_json["IMEI"],
                                       get_json["IPv4"],
                                       get_json["IPv6"],
                                       get_json["FQDN"]))
                pg.commit()
                pg_cur.execute("""INSERT INTO history("Start_time", "Previous", "DNS_ID", "Domain_ID", "Cell_ID", "Device_ID", "IMEI", "IPv4", "IPv6", "FQDN")
                                    VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}' ,'{}' ,'{}');"""
                               .format(datetime.datetime.now().replace(microsecond=0).astimezone().isoformat(),
                                       "New Connection",
                                       get_json["DNS_ID"],
                                       get_json["Domain_ID"],
                                       get_json["Cell_ID"],
                                       get_json["Device_ID"],
                                       get_json["IMEI"],
                                       get_json["IPv4"],
                                       get_json["IPv6"],
                                       get_json["FQDN"]))
                pg.commit()
            except KeyError as error:
                pg.close()
                return_json["parameter"] = str(error).replace("'", '')
                return_json["message"] = "Missing " + \
                    str(error).replace("'", '')
                return json.dumps(return_json), status.HTTP_400_BAD_REQUEST

            pg.close()
            return_json["message"] = "Create success"
            return json.dumps(return_json), status.HTTP_201_CREATED
    elif request.method == 'GET':
        Domain_ID = request.args.get('Domain_ID')
        Cell_ID = request.args.get('Cell_ID')
        pg = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                              user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
        pg_cur = pg.cursor()
        return_json = {}
        if Domain_ID == "" and Cell_ID == "":
            sql_query = ""
        elif Domain_ID != "":
            if Cell_ID == "":
                sql_query = """WHERE "Domain_ID" = '{}'""".format(Domain_ID)
            else:
                sql_query = """WHERE "Domain_ID" = '{}' AND "Cell_ID" = '{}'""".format(
                    Domain_ID, Cell_ID)
        else:
            sql_query = """WHERE "Cell_ID" = '{}'""".format(Cell_ID)

        pg_cur.execute("""SELECT * FROM current {};""".format(sql_query))
        sql_data = pg_cur.fetchall()
        pg.close()
        return_json["amount"] = len(sql_data)
        return_json["items"] = []
        for raw in sql_data:
            items_json = {}
            items_json["Datetime"] = str(
                raw[0].astimezone(tz_8).replace(tzinfo=None))
            items_json["DNS_ID"] = raw[1]
            items_json["Domain_ID"] = raw[2]
            items_json["Cell_ID"] = raw[3]
            items_json["Device_ID"] = raw[4]
            items_json["IMEI"] = raw[5]
            items_json["IPv4"] = raw[6]
            items_json["IPv6"] = raw[7]
            items_json["FQDN"] = raw[8]
            return_json["items"].append(items_json)

        return json.dumps(return_json), status.HTTP_200_OK
    else:
        IMEI = request.args.get("IMEI")
        pg = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                              user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
        return_json = {}
        pg_cur = pg.cursor()
        pg_cur.execute(
                """SELECT * FROM current WHERE "IMEI" = '{}'""".format(IMEI))
        sql_data = pg_cur.fetchall()
        
        if len(sql_data) != 0:
            pg_cur.execute(
                """DELETE FROM current WHERE "IMEI" = '{}'""".format(IMEI))
            pg.commit()

            pg_cur.execute("""UPDATE history SET "End_time" = '{}', "Next" = '{}' WHERE "Start_time" = '{}';"""
                        .format(datetime.datetime.now().replace(microsecond=0).astimezone().isoformat(),
                                "Get offline",
                                sql_data[0][0]))
            pg.commit()

            pg.close()
            return_json["message"] = "Delete success"
            return json.dumps(return_json), status.HTTP_200_OK
        else:
            pg.close()
            return_json["message"] = "Error IMEI"
            return json.dumps(return_json), status.HTTP_400_BAD_REQUEST


@app.route('/call_flow_log', methods=['POST', 'GET'])
@cross_origin()
def call_flow():
    if request.method == 'POST':
        get_json = request.json
        pg = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                              user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
        pg_cur = pg.cursor()
        return_json = {}
        try:
            pg_cur.execute("""INSERT INTO call_flow("Datetime", "Type", "Payload") 
                                VALUES('{}', '{}', '{}');"""
                           .format(datetime.datetime.now().replace(microsecond=0).astimezone().isoformat(),
                                   get_json["Type"],
                                   get_json["Payload"]))
        except KeyError as error:
            pg.close()
            return_json["parameter"] = str(error).replace("'", '')
            return_json["message"] = "Missing " + str(error).replace("'", '')
            return json.dumps(return_json), status.HTTP_400_BAD_REQUEST

        pg.commit()
        pg.close()
        return_json["message"] = "Upload success"
        return json.dumps(return_json), status.HTTP_200_OK
    else:
        pg = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                              user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
        pg_cur = pg.cursor()
        return_json = {}
        Start_time = request.args.get('Start_time')
        End_time = request.args.get('End_time')
        pg_cur.execute("""SELECT * FROM call_flow WHERE "Datetime" BETWEEN '{}' AND '{}'"""
                       .format(datetime.datetime.strptime(Start_time, "%Y-%m-%dT%H:%M%z"),
                               datetime.datetime.strptime(End_time, "%Y-%m-%dT%H:%M%z")))
        sql_data = pg_cur.fetchall()
        pg.close()
        return_json["amount"] = len(sql_data)
        return_json["items"] = []
        for raw in sql_data:
            items_json = {}
            items_json["Datetime"] = str(
                raw[0].astimezone(tz_8).replace(tzinfo=None))
            items_json["Type"] = raw[1]
            items_json["Payload"] = raw[2]
            return_json["items"].append(items_json)
        return json.dumps(return_json), status.HTTP_200_OK


@app.route('/system_log', methods=['POST', 'GET'])
@cross_origin()
def system_log():
    if request.method == 'POST':
        get_json = request.json
        pg = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                              user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
        pg_cur = pg.cursor()
        return_json = {}
        try:
            pg_cur.execute("""INSERT INTO system_log("Datetime", "DNS_env_info", "DNS_ID", "CPU_Usage", "Memory_Usage", "Disk_Usage") 
                                VALUES('{}', '{}', '{}', {}, {}, {});"""
                           .format(datetime.datetime.now().replace(microsecond=0).astimezone().isoformat(),
                                   get_json["DNS_env_info"],
                                   get_json["DNS_ID"],
                                   get_json["CPU_Usage"],
                                   get_json["Memory_Usage"],
                                   get_json["Disk_Usage"]))
        except KeyError as error:
            pg.close()
            return_json["parameter"] = str(error).replace("'", '')
            return_json["message"] = "Missing " + str(error).replace("'", '')
            return json.dumps(return_json), status.HTTP_400_BAD_REQUEST

        pg.commit()
        pg.close()
        return_json["message"] = "Upload success"
        return json.dumps(return_json), status.HTTP_200_OK
    else:
        pg = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                              user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
        pg_cur = pg.cursor()
        return_json = {}
        Start_time = request.args.get('Start_time')
        End_time = request.args.get('End_time')
        pg_cur.execute("""SELECT * FROM system_log WHERE "Datetime" BETWEEN '{}' AND '{}'"""
                       .format(datetime.datetime.strptime(Start_time, "%Y-%m-%dT%H:%M%z"),
                               datetime.datetime.strptime(End_time, "%Y-%m-%dT%H:%M%z")))
        sql_data = pg_cur.fetchall()
        pg.close()
        return_json["amount"] = len(sql_data)
        return_json["items"] = []
        for raw in sql_data:
            items_json = {}
            items_json["Datetime"] = str(
                raw[0].astimezone(tz_8).replace(tzinfo=None))
            items_json["DNS_env_info"] = raw[1]
            items_json["CPU_Usage"] = raw[2]
            items_json["Memory_Usage"] = raw[3]
            items_json["Disk_Usage"] = raw[4]
            return_json["items"].append(items_json)
        return json.dumps(return_json), status.HTTP_200_OK


@app.route('/history', methods=['GET'])
@cross_origin()
def history():
    pg = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                          user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
    pg_cur = pg.cursor()
    return_json = {}
    Start_time = request.args.get('Start_time')
    End_time = request.args.get('End_time')
    Cell_ID = request.args.get('Cell_ID')
    if Cell_ID == "":
        pg_cur.execute("""SELECT * FROM history WHERE "Start_time" > '{}' AND "End_time" < '{}'"""
                       .format(datetime.datetime.strptime(Start_time, "%Y-%m-%dT%H:%M%z"),
                               datetime.datetime.strptime(End_time, "%Y-%m-%dT%H:%M%z")))
    else:
        pg_cur.execute("""SELECT * FROM history WHERE "Cell_ID" = '{}' AND "Start_time" > '{}' AND "End_time" < '{}'"""
                       .format(Cell_ID,
                               datetime.datetime.strptime(
                                   Start_time, "%Y-%m-%dT%H:%M%z"),
                               datetime.datetime.strptime(End_time, "%Y-%m-%dT%H:%M%z")))
    sql_data = pg_cur.fetchall()
    pg.close()
    return_json["amount"] = len(sql_data)
    return_json["items"] = []

    for raw in sql_data:
        items_json = {}
        items_json["Start_time"] = str(
            raw[0].astimezone(tz_8).replace(tzinfo=None))
        items_json["End_time"] = str(
            raw[1].astimezone(tz_8).replace(tzinfo=None))
        items_json["Previous"] = raw[2]
        items_json["Next"] = raw[3]
        items_json["DNS_ID"] = raw[4]
        items_json["Domain_ID"] = raw[5]
        items_json["Cell_ID"] = raw[6]
        items_json["Device_ID"] = raw[7]
        items_json["IMEI"] = raw[8]
        items_json["IPv4"] = raw[9]
        items_json["IPv6"] = raw[10]
        items_json["FQDN"] = raw[11]
        return_json["items"].append(items_json)
    return json.dumps(return_json), status.HTTP_200_OK


@app.route('/cell_amount', methods=['GET'])
@cross_origin()
def cell_amount():
    pg = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                          user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
    pg_cur = pg.cursor()
    return_json = {}
    pg_cur.execute("""SELECT * FROM current WHERE "Cell_ID" = 'Cell_1'""")
    sql_data = pg_cur.fetchall()
    return_json["Cell_1"] = len(sql_data)
    pg_cur.execute("""SELECT * FROM current WHERE "Cell_ID" = 'Cell_2'""")
    sql_data = pg_cur.fetchall()
    return_json["Cell_2"] = len(sql_data)
    pg_cur.execute("""SELECT * FROM current WHERE "Cell_ID" = 'Cell_3'""")
    sql_data = pg_cur.fetchall()
    return_json["Cell_3"] = len(sql_data)
    pg.close()
    return json.dumps(return_json), status.HTTP_200_OK


app.run(host="0.0.0.0", port=5000, debug=True)
