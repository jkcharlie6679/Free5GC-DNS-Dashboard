import psutil
import time
import requests

url = "http://192.168.1.233:5000/system_log"

while True:
    send_json = {}
    send_json["DNS_env_info"] = "Ubuntu 18.0.4"
    send_json["DNS_ID"] = "DNS_1"
    send_json["CPU_Usage"] = psutil.cpu_percent(1)
    send_json["Memory_Usage"] = psutil.virtual_memory().percent
    send_json["Disk_Usage"] = psutil.disk_usage('/').percent
    requests.post(url, json=send_json)
    time.sleep(300-1)
