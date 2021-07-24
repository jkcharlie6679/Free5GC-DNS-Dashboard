import datetime
tz = datetime.timezone(datetime.timedelta(hours=7))
print(datetime.datetime.now().astimezone(tz))
print()
