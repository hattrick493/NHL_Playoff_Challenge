import requests
import json
from datetime import date
from datetime import datetime
import time
import sys
# Import Google Sheets API modules
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint

# TODO: Need to fix scoreboard. When loading previous games data and
# re-uploading it the scores change to strings

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

gameList = []
seriesGoals = []
wins = []

matchupsRD1 = [["FLA", "TBL"],
               ["BOS", "TOR"],
               ["NYR", "WSH"],
               ["CAR", "NYI"],
               ["DAL", "VGK"],
               ["WPG", "COL"],
               ["VAN", "NSH"],
               ["EDM", "LAK"]]

teamsRD1 = ["FLA", "TBL", "BOS", "TOR", "NYR", "WSH", "CAR", "NYI", "DAL"
            "VGK", "WPG", "COL", "VAN", "NSH", "EDM", "LAK"]

# serviceurl = 'https://api-web.nhle.com/v1/schedule/now'
serviceurl = "https://api-web.nhle.com/v1/score/now"
# serviceurl = "https://api-web.nhle.com/v1/score/2024-04-20"

goalsLoc = "S1:Z17"
winsLoc = "B48:I55"

while True:
    # Fetch the sheet
    # get_all_records() fetches the entire sheet in JSON format.
    # pprint() provided by PrettyPrinter() beautifies the JSON response.
    sheet = client.open('NHL 2024 POOL').sheet1
    python_sheet = sheet.get_all_records()

    prevSeriesGoals = seriesGoals
    seriesGoals = sheet.get(goalsLoc)  # fetches values from a range of cells
    # Loop through the seriesGoals snd change scores from string to 
    # int. skip first row (header row) and skip first column (team 
    # name)
    for series in seriesGoals[1:]:
        for idx, goals in enumerate(series[1:]):
            if isinstance(goals, str):
                if goals == " ":
                    continue
                else:
                    newGoal = int(goals)
                    series[idx+1] = newGoal
    prevWins = wins
    wins = sheet.get(winsLoc)  # fetches values from a range of cells.

    pp = pprint.PrettyPrinter()
    pp.pprint(prevSeriesGoals)
    print("")
    pp.pprint(seriesGoals)
    # pp.pprint(seriesGoals)
    # pp.pprint(wins)

    now = str(date.today())

    r = requests.get(serviceurl)
    data = r.text
    try:
        js = json.loads(data)
    except:
        js = None

    # print(json.dumps(js, indent=4))
    prevGameList = gameList
    gameList = []
    gamesWeek = js['gameWeek']
    data = js['games']
    # print(json.dumps(gamesWeek, indent=4))
    # print(json.dumps(data, indent=4))

    # Step through the JSON data and get create key-value pairs
    for game in data:
        gameDict = {}
        homeTeam = game['homeTeam']['abbrev']
        awayTeam = game['awayTeam']['abbrev']
        gameDict['homeTeam'] = homeTeam
        gameDict['awayTeam'] = awayTeam
        # gameDict['matchup'] = homeTeam + " vs " + awayTeam
        gameDict['gameState'] = game['gameState']
        gameDict['seriesRound'] = game['seriesStatus']["seriesAbbrev"]
        gameDict['topSeed'] = game['seriesStatus']["topSeedTeamAbbrev"]
        gameDict['topSeedWins'] = game['seriesStatus']["topSeedWins"]
        gameDict['bottomSeed'] = game['seriesStatus']["bottomSeedTeamAbbrev"]
        gameDict['bottomSeedWins'] = game['seriesStatus']["bottomSeedWins"]
        gameDict['gameNumber'] = game['seriesStatus']["gameNumberOfSeries"]
        gameDict['matchup'] = gameDict['topSeed'] + ' vs ' + \
            gameDict['bottomSeed']
        if game['gameState'] == 'LIVE' or game['gameState'] == 'OFF' or \
                game['gameState'] == 'FINAL' or game['gameState'] == 'CRIT':
            gameDict['homeScore'] = game['homeTeam']['score']
            gameDict['awayScore'] = game['awayTeam']['score']
            gameDict['period'] = game["period"]
            gameDict['clock'] = game["clock"]["timeRemaining"]
            gameDict['intermission'] = game["clock"]["inIntermission"]

            for team in seriesGoals:
                if homeTeam == team[0]:
                    team[gameDict['gameNumber']] = gameDict['homeScore']
                if awayTeam == team[0]:
                    team[gameDict['gameNumber']] = gameDict['awayScore']
        gameList.append(gameDict)

        if game['gameState'] == 'FINAL':
            # If the game is over, update the wins table based on game number
            if gameDict['homeScore'] > gameDict['awayScore']:
                winner = gameDict['homeTeam']
            else:
                winner = gameDict['awayTeam']
            for match in wins:
                if match[0] == gameDict['matchup']:
                    match[gameDict['gameNumber']] = winner
                    break

    print(json.dumps(gameList, indent=4))

    now = datetime.now()
    currentTime = now.strftime("%H:%M:%S")

    if wins == prevWins:
        print(currentTime, "Win data is unchanged.\nDon't update the spreadsheet")
    else:
        sheet.update(wins, winsLoc)
        print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        print(currentTime, "New Win Data")
        print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

        # Write to the spreadsheet with the new win data

    if seriesGoals == prevSeriesGoals:
        print(currentTime, "Score data is unchanged.\nDon't update the spreadsheet")
    else:
        # Loop through the seriesGoals snd change scores from string to 
        # int. skip first row (header row) and skip first column (team 
        # name)
        for series in seriesGoals[1:]:
            for idx, goals in enumerate(series[1:]):
                if isinstance(goals, str):
                    if goals == " ":
                        continue
                    else:
                        newGoal = int(goals)
                        series[idx+1] = newGoal

        sheet.update(seriesGoals, goalsLoc)
        print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        print(currentTime, "New Score Data")
        print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        # Write to the spreadsheet with the new score data

    for game in gameList:
        keepGoing = False
        if game['gameState'] == 'FINAL':
            continue
        else:
            keepGoing = True
            break

    if not keepGoing:
        print("All games are completed")
        sys.exit()
        # Exit the program here

    time.sleep(30)
