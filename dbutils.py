from datetime import datetime
import mysql.connector
from config import dbargs
import utils

def sql_exec(sql):
    """
        W3SCHOOLS MYSQL CONNECTOR FOR MOR INFO
    """
    mydb = mysql.connector.connect(
        host=dbargs["host"],
        user=dbargs["user"],
        password=dbargs["password"],
        port=dbargs["port"],
        database=dbargs["database"],
        auth_plugin=dbargs["auth_plugin"]

    )
    mycursor = mydb.cursor()
    mycursor.execute(sql)
    mydb.commit()
    mycursor.close()
    mydb.close()
def sql_select(sql):
    mydb = mysql.connector.connect(
        host=dbargs["host"],
        user=dbargs["user"],
        password=dbargs["password"],
        port=dbargs["port"],
        database=dbargs["database"],
        auth_plugin=dbargs["auth_plugin"]

    )
    mycursor = mydb.cursor()
    mycursor.execute(sql)
    data = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    return data

def savematch(matchid, lp, account):

    date = utils.getDate()
    last_matchid, last_lp = sql_select(f"SELECT matchid, lp FROM matches ORDER BY timestamp DESC LIMIT 1 WHERE account = '{account}'")[0]
    print("savematch")
    print(last_matchid, last_lp)

    if matchid != last_matchid:
        sql_exec(f"INSERT INTO matches(date, matchid, lp, lpgain, account, timestamp) values('{date}', '{matchid}', {lp}, {lp-last_lp}, '{account}', {datetime.now().timestamp()})")

def getDailyLPGain(current_lp):
    date = utils.getDate()

    try:
        startlp = sql_select(f"SELECT lp FROM matches WHERE date = '{date}' AND account = '{utils.getNemesisAccountName()}' ORDER BY timestamp DESC LIMIT 1")[0]
        print(startlp)
    except:
        startlp = None
    if not startlp:
        startlp = sql_select(f"SELECT lp FROM matches WHERE account = '{utils.getNemesisAccountName()}' ORDER BY timestamp DESC LIMIT 1")[0]

    lpgain = current_lp - startlp
    return startlp, lpgain


def getwinslosses():
    wins = 0
    losses = 0
    try:
        lpgains = sql_select(f"SELECT lpgain FROM matches WHERE date = '{utils.getDate()}' AND account = '{utils.getNemesisAccountName()}'")[0]
        for lpgain in lpgains:
            if lpgain > 0:
                wins += 1
            else:
                losses += 1
    except:
        pass
    return wins, losses

def addcommandtostats(id, username, command):
    try:
        count = sql_select(f"SELECT count FROM command_stats WHERE id = '{id}' AND command = '{command}'")[0][0]
        print(count)
    except:
        count = None
    if count:
        sql_exec(f"UPDATE command_stats SET count = {count+1} WHERE id = '{id}' AND command = '{command}'")
    else:
        sql_exec(f"INSERT INTO command_stats(id, username, command, count) VALUES ('{id}','{username}','{command}', 1)")
