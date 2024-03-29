from datetime import datetime
import mysql.connector
from config import dbargs
import utils


def sql_exec(sql):
    if "--" in sql:
        return
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
    if "--" in sql:
        return
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

    try:
        last_matchid, last_lp = sql_select(f"SELECT matchid, lp FROM matches WHERE account = '{account}' ORDER BY timestamp DESC LIMIT 1")[0]
    except:
        last_matchid = 0
        last_lp = lp

    if matchid != last_matchid:
        if not lp:
            sql_exec(f"INSERT INTO matches(date, matchid, lp, lpgain, account, timestamp) values('{date}', '{matchid}', 0, 0, '{account}', {datetime.now().timestamp()})")
            return
        sql_exec(
            f"INSERT INTO matches(date, matchid, lp, lpgain, account, timestamp) values('{date}', '{matchid}', {lp}, {lp - last_lp}, '{account}', {datetime.now().timestamp()})")


def getDailyLPGain(current_lp):
    date = utils.getDate()

    startlp = sql_select(
        f"SELECT lp FROM matches WHERE date != '{date}' AND account = '{utils.getCurrentAccountName()}' ORDER BY timestamp DESC LIMIT 1")[
        0][0]

    lpgain = current_lp - startlp
    return startlp, lpgain


def getwinslosses():
    wins = 0
    losses = 0
    try:
        lpgains = sql_select(
            f"SELECT lpgain FROM matches WHERE date = '{utils.getDate()}' AND account = '{utils.getCurrentAccountName()}'")
        for lpgain in lpgains:
            if lpgain[0] > 0:
                wins += 1
            elif lpgain[0] < 0:
                losses += 1
    except:
        pass
    return wins, losses


def addcommandtostats(id, username, command):
    if "--" in command or ";" in command:
        print("inject tried")
        return
    try:
        count = sql_select(f"SELECT count FROM command_stats WHERE id = '{id}' AND command = '{command}'")[0][0]
    except:
        count = None
    if count:
        sql_exec(f"UPDATE command_stats SET count = {count + 1} WHERE id = '{id}' AND command = '{command}'")
    else:
        sql_exec(f"INSERT INTO command_stats(id, username, command, count) VALUES ('{id}','{username}','{command}', 1)")


def addemotes(emotesinmessage):
    date = utils.getDate()
    for emote in emotesinmessage:
        try:
            count = sql_select(f"SELECT count FROM emote_tracker WHERE name = '{emote}' and date = '{date}'")[0][0]
        except:
            count = None
        if count:
            sql_exec(f"UPDATE emote_tracker SET count = {count + 1} WHERE name = '{emote}' and date = '{date}'")
        else:
            sql_exec(f"INSERT INTO emote_tracker(name, count, date) VALUES ('{emote}', 1, '{date}')")
