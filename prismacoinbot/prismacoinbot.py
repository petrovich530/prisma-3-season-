import sqlite3
import paramiko
import disnake
from disnake.ext import commands

intents  = disnake.Intents.all()

activity = disnake.Activity(
    name="My activity",
    type=disnake.ActivityType.watching,
)

bot = commands.Bot(intents=intents, activity=disnake.Game(name="prismacoin"))

@bot.event
async def on_ready():
    print("МИР-Ф")

@bot.slash_command(name="coins", description="Узнать баланс человека")
async def coins(inter: disnake.ApplicationCommandInteraction, user: str):

    hostname='хост'
    port=2022
    username='тык'
    password='тык'
    remote_path='player_times.sqlite'
    local_path='player_times.sqlite'

    try:
        transport = paramiko.Transport((hostname, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        sftp.get(remote_path, local_path)
        print(f"Файл успешно скачан и сохранен как '{local_path}'")
        
        sftp.close()
        transport.close()
    except Exception as e:
        await inter.response.send_message(f"Произошла ошибка при скачивании файла: {e}")
    
    connection = sqlite3.connect('player_times.sqlite')
    cursor = connection.cursor()
    query="SELECT total_time FROM player_times WHERE name LIKE '%' || ? || '%'"
    cursor.execute(query, (user,))
    time_minecraft=cursor.fetchall()
    connection.close()
    connection = sqlite3.connect('bot.sqlite')
    cursor = connection.cursor()
    cursor.execute('SELECT coin FROM coins WHERE nameds = :name', {"name": user})
    time_bot=cursor.fetchall()
    connection.close()
    if time_minecraft or time_bot:
        if time_minecraft and time_bot:
            for minecraft in time_minecraft[0]:
                minecraft=int(minecraft)
            for time in time_bot[0]:
                time=int(time)
            await inter.response.send_message(f"У **{user}** {time+minecraft/10} prismacoin")
        else:
            if time_bot:
                for time in time_bot[0]:
                    time=int(time)
                await inter.response.send_message(f"У **{user}** {time} prismacoin")
            else:
                for minecraft in time_minecraft[0]:
                    minecraft=int(minecraft)
                await inter.response.send_message(f"У **{user}** {minecraft/10} prismacoin")
    else:
        await inter.response.send_message("Пусть на сервер зайдёт.")

@bot.slash_command(name="coinsadd", description="Дать/отнять(доступно не всем)")
async def coinsadd(inter: disnake.ApplicationCommandInteraction, name: str, count: int):
    global result
    result=[]
    result.append(name)
    result.append(count)
    await inter.response.send_message(f"Вы хотите {count} prismacoin {name}?", components=[disnake.ui.Button(label="Да", style=disnake.ButtonStyle.success, custom_id="yes"), disnake.ui.Button(label="Нет", style=disnake.ButtonStyle.danger, custom_id="no"),],)

@bot.listen("on_button_click")
async def help_listener(inter: disnake.MessageInteraction):
    if inter.component.custom_id not in ["yes", "no"]:
        return
    if inter.component.custom_id == "yes":
        if inter.id == 527523932803301377:
            name=result[0]
            count=result[1]
            connection = sqlite3.connect('bot.sqlite')
            cursor = connection.cursor()
            cursor.execute('SELECT coin FROM coins WHERE nameds = :name', {"name": name})
            coin=cursor.fetchall()
            if coin:
                for coin in coin[0]:
                    coin=int(coin)
                coin_final=coin + count
                cursor.execute('Update coins set coin = :t where nameds = :i', {"t": coin_final, "i": name})
                connection.commit()
                connection.close()
                await inter.response.send_message("Успех")
            else:
                cursor.execute("INSERT INTO coins (nameds, coin) VALUES (:name, :count)",{"name": name, "count": count})
                connection.commit()
                connection.close()
                await inter.response.send_message("Успех")
        else:
            await inter.response.send_message("Видел, как бегемотики моргают?")
    elif inter.component.custom_id == "no":
        await inter.response.send_message("Лааааааааааадненько")

bot.run("MTIwMjkyOTQwNTA5NDI3MzA2NQ.GaQn_q.LbILITb91LpTCGnN8DZFYufDFGjh6xenLbrG9k")