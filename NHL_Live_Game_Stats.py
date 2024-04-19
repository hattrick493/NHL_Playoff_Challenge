import requests
import json
from datetime import date
# Import Google Sheets API modules
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint

# Authorize the API by creating the ServiceAccountCredentials and
# passing the JSON file client_key.json
# Using ‘gspread’ we will authorize the API.

scope = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
    ]
file_name = 'client_key.json'
creds = ServiceAccountCredentials.from_json_keyfile_name(file_name, scope)
client = gspread.authorize(creds)

matchupsRD1 = [["FLA", "TBL"],
               ["BOS", "TOR"],
               ["NYR", "WSH"],
               ["CAR", "NYI"],
               ["DAL", "LAK"],
               ["WPG", "COL"],
               ["VAN", "NSH"],
               ["EDM", "VGK"]]

# Fetch the sheet
sheet = client.open('NHL 2024 POOL').sheet1
python_sheet = sheet.get_all_records()
series_goals = sheet.get("S1:AB17")  # fetches all values from a range of cells.
wins = sheet.get("B48:I55")  # fetches all values from a range of cells.
pp = pprint.PrettyPrinter()
# pp.pprint(python_sheet)

pp.pprint(series_goals)
pp.pprint(wins)
# get_all_records() fetches the entire sheet in JSON format.
# pprint() provided by PrettyPrinter() beautifies the JSON response.
now = str(date.today())
# serviceurl = 'https://api-web.nhle.com/v1/schedule/now'
serviceurl = "https://api-web.nhle.com/v1/score/now"

r = requests.get(serviceurl)
data = r.text

try:
    js = json.loads(data)
except:
    js = None

# print(json.dumps(js, indent=4))
game_list = []
games_week = js['gameWeek']
data = js['games']

# print(json.dumps(games_week, indent=4))
# print(json.dumps(data, indent=4))

'''
Known Game State Types:
LIVE
OFF
FINAL
PRE
'''

# Step through the JSON data and get create key-value pairs
for game in data:
    game_dict = {}
    game_dict['hometeam'] = game['homeTeam']['abbrev']
    game_dict['awayteam'] = game['awayTeam']['abbrev']
    game_dict['gamestate'] = game['gameState']
    game_dict['matchup'] = game['homeTeam']['abbrev'] + " vs " + game['awayTeam']['abbrev']
    if game['gameState'] == 'LIVE' or game['gameState'] == 'OFF' or game['gameState'] == 'FINAL':
        game_dict['homescore'] = game['homeTeam']['score']
        game_dict['awayscore'] = game['awayTeam']['score']
        game_dict['period'] = game["period"]
        game_dict['clock'] = game["clock"]["timeRemaining"]
        game_dict['intermission'] = game["clock"]["inIntermission"]
    game_list.append(game_dict)

print(json.dumps(game_list, indent=4))

# print(type(js['gameWeek']))
# for day in js['gameWeek']:
#     if day['date'] == now:
#         print(json.dumps(day, indent=4))

# print(json.dumps(js, indent=4))
