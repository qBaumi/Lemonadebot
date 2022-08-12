import utils, dbutils

stats = utils.getCommandStats()
for user in stats:
    name = stats[user]["username"]
    for command in stats[user]:
        if command != "username":
            count = stats[user][command]
            try:
                dbutils.sql_exec(f"INSERT INTO command_stats(id, username, command, count) VALUES ('{user}','{name}','{command}',{count})")
            except:
                pass