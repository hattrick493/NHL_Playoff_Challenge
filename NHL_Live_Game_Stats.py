import requests
# You need to install the requests module to use this code
import json
from datetime import date

now = str(date.today())
serviceurl = 'https://api-web.nhle.com/v1/schedule/now'

r = requests.get(serviceurl)
data = r.text
print('Retrieved', len(data), 'characters')

try:
    js = json.loads(data)
except:
    js = None

print(type(js['gameWeek']))
for day in js['gameWeek']:
    if day['date'] == now:
        print(day['date'], "TRUE")

print(json.dumps(js['gameWeek'], indent=4))

   
