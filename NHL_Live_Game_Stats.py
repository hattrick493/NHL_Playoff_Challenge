import requests
# You need to install the requests module to use this code
import json
from datetime import date

now = str(date.today())
# serviceurl = 'https://api-web.nhle.com/v1/schedule/now'
serviceurl = "https://api-web.nhle.com/v1/score/now"

r = requests.get(serviceurl)
data = r.text
print('Retrieved', len(data), 'characters')


try:
    js = json.loads(data)
except:
    js = None

game_list = []

games_week = js['gameWeek']
data = js['games']
print(json.dumps(games_week, indent=4))
print(json.dumps(data, indent=4))
for game in data:
    game_dict = {}
    hometeam = game['homeTeam']['abbrev']
    awayteam = game['awayTeam']['abbrev']
    game_dict['hometeam'] = hometeam
    game_dict['awayteam'] = awayteam
    if game['gameState'] == 'LIVE' or game['gameState'] == 'OFF':
        homescore = game['homeTeam']['score']
        awayscore = game['awayTeam']['score']
        game_dict['homescore'] = homescore
        game_dict['awayscore'] = awayscore
    game_list.append(game_dict)
    # if game['gameState'] == 'LIVE':
        # print(hometeam, 'VS', awayteam)
        # print('', homescore, '   ', awayscore)

print(json.dumps(game_list, indent=4))

# print(type(js['gameWeek']))
# for day in js['gameWeek']:
#     if day['date'] == now:
#         print(json.dumps(day, indent=4))

#print(json.dumps(js, indent=4))