import json
import os
import configparser
import datetime
import psycopg2
from flask import *
from flask_api import status
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


@app.route('/resourceUsage', methods=['GET'])
def resourceUsage():
    pgSql = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                             user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
    pgCur = pgSql.cursor()
    returnJson = []
    pgCur.execute(
        """SELECT DISTINCT ON ("DNS_ID") * FROM system_log ORDER BY "DNS_ID", "Datetime" DESC""")
    sqlData = pgCur.fetchall()
    pgSql.close()

    for raw in sqlData:
        itemJson = {}
        itemJson["dnsId"] = raw[2]
        itemJson["cpuUsage"] = raw[3]
        itemJson["memoryUsage"] = raw[4]
        itemJson["diskUsage"] = raw[5]
        returnJson.append(itemJson)

    return json.dumps(returnJson), status.HTTP_200_OK


@app.route('/current', methods=['POST', 'GET', 'DELETE'])
def current():
    pgSql = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                             user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
    pgCur = pgSql.cursor()
    returnJson = {}
    if request.method == 'POST':
        getJson = request.json

        try:
            pgCur.execute(
                """SELECT * FROM current WHERE "IMEI" = '{}'""".format(getJson["IMEI"]))
        except KeyError as error:
            pgSql.close()
            returnJson["parameter"] = str(error).replace("'", '')
            returnJson["message"] = "Missing " + str(error).replace("'", '')
            return json.dumps(returnJson), status.HTTP_400_BAD_REQUEST
        sqlData = pgCur.fetchall()
        if len(sqlData) == 1:
            try:
                pgCur.execute("""UPDATE current SET "Start_time" = '{}',
                                                    "DNS_ID" = '{}',
                                                    "Domain_ID" = '{}',
                                                    "Cell_ID" = '{}',
                                                    "Device_ID" = '{}',
                                                    "IMEI" = '{}',
                                                    "IPv4" = '{}',
                                                    "IPv6"= '{}',
                                                    "FQDN" = '{}' WHERE "IMEI" = '{}';"""
                              .format(datetime.datetime.now().replace(microsecond=0).astimezone().isoformat(),
                                      getJson["DNS_ID"],
                                      getJson["Domain_ID"],
                                      getJson["Cell_ID"],
                                      getJson["Device_ID"],
                                      getJson["IMEI"],
                                      getJson["IPv4"],
                                      getJson["IPv6"],
                                      getJson["FQDN"],
                                      getJson["IMEI"]))
                pgSql.commit()
                pgCur.execute("""UPDATE history SET "End_time" = '{}', "Next" = '{}' WHERE "Start_time" = '{}';"""
                              .format(datetime.datetime.now().replace(microsecond=0).astimezone().isoformat(),
                                      "Hand off to " + getJson["Cell_ID"],
                                      sqlData[0][0]))
                pgSql.commit()
                pgCur.execute("""INSERT INTO history("Start_time", "Previous", "DNS_ID", "Domain_ID", "Cell_ID", "Device_ID", "IMEI", "IPv4", "IPv6", "FQDN")
                                    VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}' ,'{}' ,'{}');"""
                              .format(datetime.datetime.now().replace(microsecond=0).astimezone().isoformat(),
                                      "Hand off from " + sqlData[0][3],
                                      getJson["DNS_ID"],
                                      getJson["Domain_ID"],
                                      getJson["Cell_ID"],
                                      getJson["Device_ID"],
                                      getJson["IMEI"],
                                      getJson["IPv4"],
                                      getJson["IPv6"],
                                      getJson["FQDN"]))
                pgSql.commit()
            except KeyError as error:
                pgSql.close()
                returnJson["parameter"] = str(error).replace("'", '')
                returnJson["message"] = "Missing " + \
                    str(error).replace("'", '')
                return json.dumps(returnJson), status.HTTP_400_BAD_REQUEST
            pgSql.close()
            returnJson["message"] = "Update success"
            return json.dumps(returnJson), status.HTTP_200_OK
        else:
            try:
                pgCur.execute("""INSERT INTO current("Start_time", "DNS_ID", "Domain_ID", "Cell_ID", "Device_ID", "IMEI", "IPv4", "IPv6", "FQDN")
                                    VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}' ,'{}' ,'{}');"""
                              .format(datetime.datetime.now().replace(microsecond=0).astimezone().isoformat(),
                                      getJson["DNS_ID"],
                                      getJson["Domain_ID"],
                                      getJson["Cell_ID"],
                                      getJson["Device_ID"],
                                      getJson["IMEI"],
                                      getJson["IPv4"],
                                      getJson["IPv6"],
                                      getJson["FQDN"]))
                pgSql.commit()
                pgCur.execute("""INSERT INTO history("Start_time", "Previous", "DNS_ID", "Domain_ID", "Cell_ID", "Device_ID", "IMEI", "IPv4", "IPv6", "FQDN")
                                    VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}' ,'{}' ,'{}');"""
                              .format(datetime.datetime.now().replace(microsecond=0).astimezone().isoformat(),
                                      "New Connection",
                                      getJson["DNS_ID"],
                                      getJson["Domain_ID"],
                                      getJson["Cell_ID"],
                                      getJson["Device_ID"],
                                      getJson["IMEI"],
                                      getJson["IPv4"],
                                      getJson["IPv6"],
                                      getJson["FQDN"]))
                pgSql.commit()
            except KeyError as error:
                pgSql.close()
                returnJson["parameter"] = str(error).replace("'", '')
                returnJson["message"] = "Missing " + \
                    str(error).replace("'", '')
                return json.dumps(returnJson), status.HTTP_400_BAD_REQUEST

            pgSql.close()
            returnJson["message"] = "Create success"
            return json.dumps(returnJson), status.HTTP_201_CREATED
    elif request.method == 'GET':
        domainId = request.args.get('domainId')
        cellId = request.args.get('cellId')
        if domainId == "" and cellId == "":
            sql_query = ""
        elif domainId != "":
            if cellId == "":
                sql_query = """WHERE "Domain_ID" = '{}'""".format(domainId)
            else:
                sql_query = """WHERE "Domain_ID" = '{}' AND "Cell_ID" = '{}'""".format(
                    domainId, cellId)
        else:
            sql_query = """WHERE "Cell_ID" = '{}'""".format(cellId)

        pgCur.execute("""SELECT * FROM current {};""".format(sql_query))
        sqlData = pgCur.fetchall()
        pgSql.close()
        returnJson["amount"] = len(sqlData)
        returnJson["items"] = []
        for raw in sqlData:
            itemJson = {}
            itemJson["datetime"] = str(
                raw[0].astimezone(timezone8).replace(tzinfo=None))
            itemJson["dnsId"] = raw[1]
            itemJson["domainId"] = raw[2]
            itemJson["cellId"] = raw[3]
            itemJson["deviceId"] = raw[4]
            itemJson["imei"] = raw[5]
            itemJson["ipv4"] = raw[6]
            itemJson["ipv6"] = raw[7]
            itemJson["fqdn"] = raw[8]
            returnJson["items"].append(itemJson)

        return json.dumps(returnJson), status.HTTP_200_OK
    elif request.method == 'DELETE':
        imei = request.args.get("IMEI")
        pgCur.execute(
            """SELECT * FROM current WHERE "IMEI" = '{}'""".format(imei))
        sqlData = pgCur.fetchall()

        if len(sqlData) != 0:
            pgCur.execute(
                """DELETE FROM current WHERE "IMEI" = '{}'""".format(imei))
            pgSql.commit()

            pgCur.execute("""UPDATE history SET "End_time" = '{}', "Next" = '{}' WHERE "Start_time" = '{}';"""
                          .format(datetime.datetime.now().replace(microsecond=0).astimezone().isoformat(),
                                  "Get offline",
                                  sqlData[0][0]))
            pgSql.commit()

            pgSql.close()
            returnJson["message"] = "Delete success"
            return json.dumps(returnJson), status.HTTP_200_OK
        else:
            pgSql.close()
            returnJson["message"] = "Error IMEI"
            return json.dumps(returnJson), status.HTTP_400_BAD_REQUEST


@app.route('/call_flow_log', methods=['POST', 'GET'])
def callFlow():
    pgSql = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                             user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
    pgCur = pgSql.cursor()
    returnJson = {}
    if request.method == 'POST':
        getJson = request.json
        try:
            pgCur.execute("""INSERT INTO call_flow("Datetime", "Type", "Payload") 
                                VALUES('{}', '{}', '{}');"""
                          .format(datetime.datetime.now().replace(microsecond=0).astimezone().isoformat(),
                                  getJson["Type"],
                                  getJson["Payload"]))
        except KeyError as error:
            pgSql.close()
            returnJson["parameter"] = str(error).replace("'", '')
            returnJson["message"] = "Missing " + str(error).replace("'", '')
            return json.dumps(returnJson), status.HTTP_400_BAD_REQUEST

        pgSql.commit()
        pgSql.close()
        returnJson["message"] = "Upload success"
        return json.dumps(returnJson), status.HTTP_200_OK
    elif request.method == 'GET':
        startTime = request.args.get('startTime')
        endTime = request.args.get('endTime')
        pgCur.execute("""SELECT * FROM call_flow WHERE "Datetime" BETWEEN '{}' AND '{}' ORDER BY "Datetime" ASC;"""
                      .format(datetime.datetime.strptime(startTime, "%Y-%m-%dT%H:%M%z"),
                              datetime.datetime.strptime(endTime, "%Y-%m-%dT%H:%M%z")))
        sqlData = pgCur.fetchall()
        pgSql.close()
        returnJson["amount"] = len(sqlData)
        returnJson["items"] = []
        for raw in sqlData:
            itemJson = {}
            itemJson["type"] = raw[1]
            itemJson["datetime"] = str(
                raw[0].astimezone(timezone8).replace(tzinfo=None))
            itemJson["payload"] = raw[2]
            returnJson["items"].append(itemJson)
        return json.dumps(returnJson), status.HTTP_200_OK


@app.route('/system_log', methods=['POST', 'GET'])
def systemLog():
    pgSql = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                             user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
    pgCur = pgSql.cursor()
    returnJson = {}
    if request.method == 'POST':
        getJson = request.json
        try:
            pgCur.execute("""INSERT INTO system_log("Datetime", "DNS_env_info", "DNS_ID", "CPU_Usage", "Memory_Usage", "Disk_Usage") 
                                VALUES('{}', '{}', '{}', {}, {}, {});"""
                          .format(datetime.datetime.now().replace(microsecond=0).astimezone().isoformat(),
                                  getJson["DNS_env_info"],
                                  getJson["DNS_ID"],
                                  getJson["CPU_Usage"],
                                  getJson["Memory_Usage"],
                                  getJson["Disk_Usage"]))
        except KeyError as error:
            pgSql.close()
            returnJson["parameter"] = str(error).replace("'", '')
            returnJson["message"] = "Missing " + str(error).replace("'", '')
            return json.dumps(returnJson), status.HTTP_400_BAD_REQUEST

        pgSql.commit()
        pgSql.close()
        returnJson["message"] = "Upload success"
        return json.dumps(returnJson), status.HTTP_200_OK
    elif request.method == 'GET':
        startTimr = request.args.get('startTime')
        endTime = request.args.get('endTime')
        pgCur.execute("""SELECT * FROM system_log WHERE "Datetime" BETWEEN '{}' AND '{}' ORDER BY "Datetime" ASC;"""
                      .format(datetime.datetime.strptime(startTimr, "%Y-%m-%dT%H:%M%z"),
                              datetime.datetime.strptime(endTime, "%Y-%m-%dT%H:%M%z")))
        sqlData = pgCur.fetchall()
        pgSql.close()
        returnJson["amount"] = len(sqlData)
        returnJson["items"] = []
        for raw in sqlData:
            itemJson = {}
            itemJson["datetime"] = str(
                raw[0].astimezone(timezone8).replace(tzinfo=None))
            itemJson["dnsEnvInfo"] = raw[1]
            itemJson["dnsId"] = raw[2]
            itemJson["cpuUsage"] = raw[3]
            itemJson["memoryUsage"] = raw[4]
            itemJson["diskUsage"] = raw[5]
            returnJson["items"].append(itemJson)
        return json.dumps(returnJson), status.HTTP_200_OK


@app.route('/deviceId', methods=['GET'])
def getDeviceId():
    pgSql = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                             user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
    pgCur = pgSql.cursor()
    pgCur.execute("""SELECT DISTINCT "Device_ID" FROM "history";""")
    sqlData = pgCur.fetchall()
    pgSql.close()
    returnJson = {}
    returnJson["deviceId"] = []
    for item in sqlData:
        returnJson["deviceId"].append(item[0])

    return json.dumps(returnJson), status.HTTP_200_OK


@app.route('/history', methods=['GET'])
def history():
    pgSql = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                             user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
    pgCur = pgSql.cursor()
    returnJson = {}
    startTime = request.args.get('startTime')
    endTime = request.args.get('endTime')
    cellId = request.args.get('cellId')
    deviceId = request.args.get('deviceId')
    if cellId == "" and deviceId == "":
        pgCur.execute("""SELECT * FROM history WHERE "Start_time" > '{}' AND "End_time" < '{}' ORDER BY "Start_time" ASC;"""
                      .format(datetime.datetime.strptime(startTime, "%Y-%m-%dT%H:%M%z"),
                              datetime.datetime.strptime(endTime, "%Y-%m-%dT%H:%M%z")))
    elif deviceId == "":
        pgCur.execute("""SELECT * FROM history WHERE "Cell_ID" = '{}' AND "Start_time" > '{}' AND "End_time" < '{}' ORDER BY "Start_time" ASC;"""
                      .format(cellId,
                              datetime.datetime.strptime(
                                  startTime, "%Y-%m-%dT%H:%M%z"),
                              datetime.datetime.strptime(endTime, "%Y-%m-%dT%H:%M%z")))
    elif cellId == "":
        pgCur.execute("""SELECT * FROM history WHERE "Device_ID" = '{}' AND "Start_time" > '{}' AND "End_time" < '{}' ORDER BY "Start_time" ASC;"""
                      .format(deviceId,
                              datetime.datetime.strptime(
                                  startTime, "%Y-%m-%dT%H:%M%z"),
                              datetime.datetime.strptime(endTime, "%Y-%m-%dT%H:%M%z")))
    else:
        pgCur.execute("""SELECT * FROM history WHERE "Cell_ID" = '{}' AND "Device_ID" = '{}' AND "Start_time" > '{}' AND "End_time" < '{}' ORDER BY "Start_time" ASC;"""
                      .format(cellId,
                              deviceId,
                              datetime.datetime.strptime(
                                  startTime, "%Y-%m-%dT%H:%M%z"),
                              datetime.datetime.strptime(endTime, "%Y-%m-%dT%H:%M%z")))
    sqlData = pgCur.fetchall()
    pgSql.close()
    returnJson["amount"] = len(sqlData)
    returnJson["items"] = []

    for raw in sqlData:
        itemJson = {}
        itemJson["startTime"] = str(
            raw[0].astimezone(timezone8).replace(tzinfo=None))
        itemJson["endTime"] = str(
            raw[1].astimezone(timezone8).replace(tzinfo=None))
        itemJson["previous"] = raw[2]
        itemJson["next"] = raw[3]
        itemJson["dnsId"] = raw[4]
        itemJson["domainId"] = raw[5]
        itemJson["cellId"] = raw[6]
        itemJson["deviceId"] = raw[7]
        itemJson["imei"] = raw[8]
        itemJson["ipv4"] = raw[9]
        itemJson["ipv6"] = raw[10]
        itemJson["fqdn"] = raw[11]
        returnJson["items"].append(itemJson)
    return json.dumps(returnJson), status.HTTP_200_OK


@app.route('/cellAmount', methods=['GET'])
def getCellAmount():
    pgSql = psycopg2.connect(database=config['database']['database'], host=config['database']['host'],
                             user=config['database']['user'], password=config['database']['password'], port=config['database']['port'])
    pgCur = pgSql.cursor()
    returnJson = {}
    pgCur.execute("""SELECT * FROM current WHERE "Cell_ID" = 'Cell_1'""")
    sqlData = pgCur.fetchall()
    returnJson["cellOne"] = len(sqlData)
    pgCur.execute("""SELECT * FROM current WHERE "Cell_ID" = 'Cell_2'""")
    sqlData = pgCur.fetchall()
    returnJson["cellTwo"] = len(sqlData)
    pgCur.execute("""SELECT * FROM current WHERE "Cell_ID" = 'Cell_3'""")
    sqlData = pgCur.fetchall()
    returnJson["cellThree"] = len(sqlData)
    pgSql.close()
    return json.dumps(returnJson), status.HTTP_200_OK


@app.route('/dns', methods=['GET', 'POST', 'DELETE'])
def dns():
    if request.method != "GET":
        ip = request.args["IP"]
        domain = request.args["Domain"]
    returnJson = {}
    if request.method == "POST":
        with open(config['DNS']['FILE'], "r") as configFile:
            lines = configFile.readlines()
            for line in lines:
                indexIp = 0
                indexDomain = 0
                for data in line:
                    if indexIp == len(ip):
                        if data == ";":
                            break
                        else:
                            indexIp = 0
                    if data == ip[indexIp]:
                        indexIp += 1
                    else:
                        indexIp = 0

                    if indexDomain == len(domain):
                        if data == " ":
                            break
                        else:
                            indexDomain = 0
                    if data == domain[indexDomain]:
                        indexDomain += 1
                    else:
                        indexDomain = 0

                if indexIp == len(ip):
                    lines[lines.index(line)] = "{} IN A {};\n".format(
                        domain, ip)
                    returnJson["message"] = "Update sucess"
                    break
                if indexDomain == len(domain):
                    break
            if indexDomain == len(domain):
                returnJson["message"] = "Same domain"
                return json.dumps(returnJson), status.HTTP_400_BAD_REQUEST
            if indexIp != len(ip):
                lines.append("{} IN A {};\n".format(domain, ip))
                returnJson["message"] = "Create sucess"

        with open(config['DNS']['FILE'], "w") as configFile:
            configFile.writelines(lines)
        os.system("sudo systemctl reload bind9")
        if returnJson["message"] == "Create sucess":
            return json.dumps(returnJson), status.HTTP_201_CREATED
        else:
            return json.dumps(returnJson), status.HTTP_200_OK
    elif request.method == "DELETE":
        with open(config['DNS']['FILE'], "r") as configFile:
            lines = configFile.readlines()
            for line in lines:
                indexIp = 0
                for data in line:
                    if indexIp == len(ip):
                        if data == ";":
                            break
                        else:
                            indexIp = 0
                    if data == ip[indexIp]:
                        indexIp += 1
                    else:
                        indexIp = 0

                if indexIp == len(ip):
                    lines = lines[:lines.index(
                        line)] + lines[lines.index(line)+1:]
                    break

        with open(config['DNS']['FILE'], "w") as configFile:
            configFile.writelines(lines)
            returnJson["message"] = "Delete sucess"
        os.system("sudo systemctl reload bind9")
        return json.dumps(returnJson), status.HTTP_200_OK
    elif request.method == "GET":
        search = "localhost.;"
        filterWord = " IN A "

        with open(config['DNS']['FILE'], 'r') as theFile:
            lines = theFile.readlines()

            for line in lines:
                indexWord = 0
                for word in line:
                    if indexWord == len(search):
                        break
                    if word == search[indexWord]:
                        indexWord += 1
                    else:
                        indexWord = 0
                if indexWord == len(search):
                    start_line = lines.index(line) + 1
                    break
            returnJson["amount"] = len(lines[start_line:])
            returnJson["items"] = []
            for line in lines[start_line:]:
                itemJson = {}
                filter_start = line.index(filterWord)
                itemJson["Domain"] = line[:filter_start]+".free5gc"
                itemJson["ip"] = line.replace(";\n", "")[filter_start+6:]
                returnJson["items"].append(itemJson)

        return json.dumps(returnJson), status.HTTP_200_OK


if __name__ == "__main__":
    cfgpath = os.path.abspath('.') + "/config.ini"

    config = configparser.ConfigParser()
    config.read(cfgpath)

    timezone8 = datetime.timezone(datetime.timedelta(hours=8))

    app.run(host="0.0.0.0", port=5534, debug=True)
