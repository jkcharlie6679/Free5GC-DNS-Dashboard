import psutil
import time
import requests

url = "http://127.0.0.1:8080/systemLog"

while True:
    send_json = {}
    send_json["dnsEnvInfo"] = "Ubuntu 18.0.4"
    send_json["dnsId"] = "DNS_1"
    send_json["cpuUsage"] = psutil.cpu_percent(1)
    send_json["memoryUsage"] = psutil.virtual_memory().percent
    send_json["diskUsage"] = psutil.disk_usage('/').percent
    requests.post(url, json=send_json)
    time.sleep(300-1)
