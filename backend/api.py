import json
import os
from flask import *
from utilities import db, dnsFile, timezone8, timeNow, timeToString
from flasgger import swag_from

api = Blueprint('api', __name__)


@api.route('/resourceUsage', methods=['GET'])
@swag_from("yaml/resourceUsage.yaml", methods=['GET'])
def resourceUsage():
    sqlData = db.query('''SELECT DISTINCT ON ("dnsId") * FROM "systemLog" ORDER BY "dnsId", "datetime" DESC''')
    returnJson = []
    for raw in sqlData:
        itemJson = {}
        itemJson["dnsId"] = raw[2]
        itemJson["cpuUsage"] = raw[3]
        itemJson["memoryUsage"] = raw[4]
        itemJson["diskUsage"] = raw[5]
        returnJson.append(itemJson)

    response = Response(response=json.dumps(returnJson), status=200)
    return response



@api.route('/current', methods=['POST', 'GET', 'DELETE'])
@swag_from("yaml/currentPost.yaml", methods=['POST'])
@swag_from("yaml/currentGet.yaml", methods=['GET'])
@swag_from("yaml/currentDelete.yaml", methods=['DELETE'])
def current():
    if request.method == 'POST':
        dnsId = request.args.get("dnsId")
        domainId = request.args.get("domainId")
        cellId = request.args.get("cellId")
        deviceId = request.args.get("deviceId")
        imei = request.args.get("imei")
        ipv4 = request.args.get("ipv4")
        ipv6 = request.args.get("ipv6")
        sliceId = request.args.get("sliceId")
        fqdn = request.args.get("fqdn")

        sqlData= db.query("""SELECT * FROM "current" WHERE "imei" = %s""", imei)

        if len(sqlData) == 1:
            db.query("""UPDATE "current" SET "startTime" = %s, "dnsId" = %s, "domainId" = %s, "cellId" = %s, "deviceId" = %s, "imei" = %s, 
                        "ipv4" = %s, "ipv6"= %s, "sliceId" = %s, "fqdn" = %s  WHERE "imei" = %s;""", 
                        timeNow(), dnsId, domainId, cellId, deviceId, imei, ipv4, ipv6, sliceId, fqdn, imei)

            db.query("""UPDATE "history" SET "endTime" = %s, "next" = %s WHERE "startTime" = %s;""",
                        timeNow(), "Hand off to " + cellId, sqlData[0][0])

            db.query("""INSERT INTO "history" ("startTime", "previous", "dnsId", "domainId", "cellId", "deviceId", "imei", "ipv4", "ipv6", "sliceId", "fqdn")
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                        timeNow(), "Hand off from " + sqlData[0][3], dnsId, domainId, cellId, deviceId, imei, ipv4, ipv6, sliceId, fqdn)
            returnJson = {"message": "Update successfully"}
            return Response(response=json.dumps(returnJson), status=200)
        else:
            db.query("""INSERT INTO current("startTime", "dnsId", "domainId", "cellId", "deviceId", "imei", "ipv4", "ipv6", "sliceId", "fqdn")
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""", 
                        timeNow(), dnsId, domainId, cellId, deviceId, imei, ipv4, ipv6, sliceId, fqdn)

            db.query("""INSERT INTO history("startTime", "previous", "dnsId", "domainId", "cellId", "deviceId", "imei", "ipv4", "ipv6", "sliceId", "fqdn")
                                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                        timeNow(), "New Connection", dnsId, domainId, cellId, deviceId, imei, ipv4, ipv6, sliceId, fqdn)

            returnJson = {"message": "Create successfully"}
            return Response(response=json.dumps(returnJson), status=200)

    elif request.method == 'GET':
        domainId = request.args.get('domainId')
        cellId = request.args.get('cellId')
        if domainId == None and cellId == None:
            sqlData = db.query("""SELECT * FROM "current";""")
        elif domainId != None:
            if cellId == None:
                sqlData = db.query("""SELECT * FROM "current" WHERE "domainId" = %s;""", domainId)
            else:
                sqlData = db.query("""SELECT * FROM "current" WHERE "domainId" = %s AND "cellId" = %s;""", domainId, cellId)
        else:
            sqlData = db.query("""SELECT * FROM "current" WHERE "cellId" = %s;""", cellId)

        returnJson = {
            "amount": len(sqlData),
            "items": []
        }
        for raw in sqlData:
            itemJson = {}
            itemJson["datetime"] = str(raw[0].astimezone(timezone8).replace(tzinfo=None))
            itemJson["dnsId"] = raw[1]
            itemJson["domainId"] = raw[2]
            itemJson["cellId"] = raw[3]
            itemJson["deviceId"] = raw[4]
            itemJson["imei"] = raw[5]
            itemJson["ipv4"] = raw[6]
            itemJson["ipv6"] = raw[7]
            itemJson["sliceId"] = raw[8]
            itemJson["fqdn"] = raw[9]
            returnJson["items"].append(itemJson)

        return Response(response=json.dumps(returnJson), status=200)

    elif request.method == 'DELETE':
        imei = request.args.get("imei")
        sqlData = db.query("""SELECT * FROM "current" WHERE "imei" = %s;""", imei)

        if len(sqlData) != 0:
            db.query("""DELETE FROM "current" WHERE "imei" = %s;""", imei)

            db.query("""UPDATE "history" SET "endTime" = %s, "next" = %s WHERE "startTime" = %s;""",
                        timeNow(), "Get offline", sqlData[0][0])

            returnJson = {"message": "Delete successfully"}
            return Response(response=json.dumps(returnJson), status=200)
        else:
            returnJson = {"message": "Error IMEI"}
            return Response(response=json.dumps(returnJson), status=400)


@api.route('/callFlowLog', methods=['POST', 'GET'])
@swag_from("yaml/callFlowPost.yaml", methods=['POST'])
@swag_from("yaml/callFlowGet.yaml", methods=['GET'])
def callFlow():
    if request.method == 'POST':
        type = request.args.get("type")
        payload = request.args.get("payload")
        try:
            db.query("""INSERT INTO "callFlow"("datetime", "type", "payload") VALUES(%s, %s, %s);""",
                        timeNow(), type, payload)
        except KeyError as error:
            returnJson = {
                "parameter": str(error).replace("'", ''),
                "message": "Missing " + str(error).replace("'", '')
            }
            return Response(response=json.dumps(returnJson), status=400)

        returnJson = {"message": "Upload successfully"}
        return Response(response=json.dumps(returnJson), status=200)
    elif request.method == 'GET':
        startTime = request.args.get('startTime')
        endTime = request.args.get('endTime')
        sqlData = db.query("""SELECT * FROM "callFlow" WHERE "datetime" BETWEEN %s AND %s ORDER BY "datetime" ASC;""",
                                timeToString(startTime), timeToString(endTime))

        returnJson = {
            "amount": len(sqlData),
            "items": []
        }
        for raw in sqlData:
            itemJson = {}
            itemJson["type"] = raw[1]
            itemJson["datetime"] = str(raw[0].astimezone(timezone8).replace(tzinfo=None))
            itemJson["payload"] = raw[2]
            returnJson["items"].append(itemJson)
        return Response(response=json.dumps(returnJson), status=200)


@api.route('/systemLog', methods=['POST', 'GET'])
@swag_from("yaml/systemLogPost.yaml", methods=['POST'])
@swag_from("yaml/systemLogGet.yaml", methods=['GET'])
def systemLog():
    if request.method == 'POST':
        getJson = request.json
        try:
            db.query('''INSERT INTO "systemLog"("datetime", "dnsEnvInfo", "dnsId", "cpuUsage", "memoryUsage", "diskUsage") 
                                VALUES(%s, %s, %s, %s, %s, %s);'''
                          ,timeNow(), getJson["dnsEnvInfo"], getJson["dnsId"], getJson["cpuUsage"], getJson["memoryUsage"], getJson["diskUsage"])
        except KeyError as error:
            returnJson = {
                "parameter": str(error).replace("'", ''),
                "message": "Missing " + str(error).replace("'", '')
                }
            return Response(response=json.dumps(returnJson), status=400)

        returnJson = {"message": "Upload successfully"}
        return Response(response=json.dumps(returnJson), status=200)

    elif request.method == 'GET':
        startTimr = request.args.get('startTime')
        endTime = request.args.get('endTime')
        sqlData = db.query("""SELECT * FROM "systemLog" WHERE "datetime" BETWEEN %s AND %s ORDER BY "datetime" ASC;""",
                                timeToString(startTimr), timeToString(endTime))

        returnJson = {
            "amount": len(sqlData),
            "items": []
        }
        for raw in sqlData:
            itemJson = {}
            itemJson["datetime"] = str(raw[0].astimezone(timezone8).replace(tzinfo=None))
            itemJson["dnsEnvInfo"] = raw[1]
            itemJson["dnsId"] = raw[2]
            itemJson["cpuUsage"] = raw[3]
            itemJson["memoryUsage"] = raw[4]
            itemJson["diskUsage"] = raw[5]
            returnJson["items"].append(itemJson)

        return Response(response=json.dumps(returnJson), status=200)


@api.route('/deviceId', methods=['GET'])
@swag_from("yaml/deviceId.yaml", methods=['GET'])
def getDeviceId():
    sqlData = db.query("""SELECT DISTINCT "deviceId" FROM "history";""")
    returnJson = {"deviceId": []}
    for item in sqlData:
        returnJson["deviceId"].append(item[0])

    return Response(response=json.dumps(returnJson), status=200)


@api.route('/history', methods=['GET'])
@swag_from("yaml/history.yaml", methods=['GET'])
def history():
    startTime = request.args.get('startTime')
    endTime = request.args.get('endTime')
    cellId = request.args.get('cellId')
    deviceId = request.args.get('deviceId')
    if cellId == None and deviceId == None:
        sqlData = db.query("""SELECT * FROM "history" WHERE "startTime" > %s AND "endTime" < %s ORDER BY "startTime" ASC;""",
                                timeToString(startTime), timeToString(endTime))
    elif deviceId == None:
        sqlData = db.query("""SELECT * FROM "history" WHERE "cellId" = %s AND "startTime" > %s AND "endTime" < %s ORDER BY "startTime" ASC;""",
                                cellId, timeToString(startTime), timeToString(endTime))
    elif cellId == None:
        sqlData = db.query("""SELECT * FROM "history" WHERE "deviceId" = %s AND "startTime" > %s AND "endTime" < %s ORDER BY "startTime" ASC;""",
                                deviceId, timeToString(startTime), timeToString(endTime))
    else:
        sqlData = db.query("""SELECT * FROM "history" WHERE "cellId" = %s AND "deviceId" = %s AND "startTime" > %s AND "endTime" < %s ORDER BY "startTime" ASC;""",
                                cellId, deviceId, timeToString(startTime), timeToString(endTime))
    returnJson = {
        "amount": len(sqlData),
        "items": []
    }

    for raw in sqlData:
        itemJson = {}
        itemJson["startTime"] = str(raw[0].astimezone(timezone8).replace(tzinfo=None))
        itemJson["endTime"] = str(raw[1].astimezone(timezone8).replace(tzinfo=None))
        itemJson["previous"] = raw[2]
        itemJson["next"] = raw[3]
        itemJson["dnsId"] = raw[4]
        itemJson["domainId"] = raw[5]
        itemJson["cellId"] = raw[6]
        itemJson["deviceId"] = raw[7]
        itemJson["imei"] = raw[8]
        itemJson["ipv4"] = raw[9]
        itemJson["ipv6"] = raw[10]
        itemJson["sliceId"] = raw[11]
        itemJson["fqdn"] = raw[12]
        returnJson["items"].append(itemJson)
    return Response(response=json.dumps(returnJson), status=200)


@api.route('/cellAmount', methods=['GET'])
@swag_from("yaml/cellAmount.yaml", methods=['GET'])
def getCellAmount():

    returnJson = {}
    sqlData = db.query("""SELECT * FROM "current" WHERE "cellId" = 'Cell_1'""")
    returnJson["cellOne"] = len(sqlData)

    sqlData = db.query("""SELECT * FROM "current" WHERE "cellId" = 'Cell_2'""")
    returnJson["cellTwo"] = len(sqlData)

    sqlData = db.query("""SELECT * FROM "current" WHERE "cellId" = 'Cell_3'""")
    returnJson["cellThree"] = len(sqlData)

    return Response(response=json.dumps(returnJson), status=200)


@api.route('/dns', methods=['GET', 'POST', 'DELETE'])
@swag_from("yaml/dnsGet.yaml", methods=['GET'])
@swag_from("yaml/dnsPost.yaml", methods=['POST'])
@swag_from("yaml/dnsDelete.yaml", methods=['DELETE'])
def dns():
    if request.method == "POST":
        ip = request.args["ip"]
        domain = request.args["domain"]
        with open(dnsFile, "r") as configFile:
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
                    returnJson = {"message": "Update sucess"}
                    break
                if indexDomain == len(domain):
                    break
            if indexDomain == len(domain):
                returnJson = {
                    "message": "Same domain"
                    }
                return Response(response=json.dumps(returnJson), status=400)
            if indexIp != len(ip):
                lines.append("{} IN A {};\n".format(domain, ip))
                returnJson = {"message": "Create sucess"}

        with open(dnsFile, "w") as configFile:
            configFile.writelines(lines)
        os.system("sudo systemctl reload bind9")
        if returnJson["message"] == "Create sucess":
            return Response(response=json.dumps(returnJson), status=201)
        else:
            return Response(response=json.dumps(returnJson), status=200)

    elif request.method == "DELETE":
        ip = request.args["ip"]
        with open(dnsFile, "r") as configFile:
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

        with open(dnsFile, "w") as configFile:
            configFile.writelines(lines)
            returnJson = {"message": "Delete sucess"}
        os.system("sudo systemctl reload bind9")
        return Response(response=json.dumps(returnJson), status=200)
    elif request.method == "GET":
        search = "localhost.;"
        filterWord = " IN A "

        with open(dnsFile, 'r') as theFile:
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
            returnJson = {
                "amount": len(lines[start_line:]),
                "items": []
                }
            for line in lines[start_line:]:
                itemJson = {}
                filter_start = line.index(filterWord)
                itemJson["domain"] = line[:filter_start]+".free5gc"
                itemJson["ip"] = line.replace(";\n", "")[filter_start+6:]
                returnJson["items"].append(itemJson)

        return Response(response=json.dumps(returnJson), status=200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5534, debug=True)
