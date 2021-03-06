#!/usr/bin/env python3
import discord
import random
import os
import ffmpeg
import time
import asyncio
from credentials import*
from yt_dl import*
from discord.ext import commands
import yfinance as yf
import requests
from discord import FFmpegPCMAudio, PCMVolumeTransformer

TOKEN = (DISCORD_TOKEN)
help_command = commands.DefaultHelpCommand(no_category = 'Commands')
bot = commands.Bot(command_prefix=commands.when_mentioned_or('#'), help_command = help_command)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    await bot.change_presence(activity=discord.Game('Discord'))

@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return
    blacklist = ["#pferdegeruch!", "Hurensohn", "Wichser"]
    msg_content = message.content.lower()
    if any(word in msg_content for word in blacklist):
        await message.delete()
    await bot.process_commands(message)

@bot.command(name='hello', help = 'Respondse Hello.')
async def hello(ctx, msg):
    await ctx.send('Hello')
    print("{}: Hello".format(ctx.message.author.name))

@bot.command(name='roll_dice', help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int=1, number_of_sides: int=6):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))
    print("{}: Hat gewürfelt. Ergebnis: ".format(ctx.message.author.name) + ', '.join(dice))

@bot.command(name='join', help='Bot joint in Channel')
async def join(ctx):
    voice_client = ctx.message.guild.voice_client
    if not ctx.message.author.voice:
        await ctx.send("{} ist in keinem Channel".format(ctx.message.author.name))
        return
    else:
        try:
            await voice_client.disconnect()
            channel = ctx.message.author.voice.channel
        except:
            channel = ctx.message.author.voice.channel
    await channel.connect()
    await ctx.send("joined {} to voice channel".format(ctx.message.author.name))
    print("{}: join channel".format(ctx.message.author.name))

@bot.command(name='leave', help='Bot verlässt Channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    try:
    	 voice_channel.stop()
    except:
    	print(" ")
    try:
       	await voice_client.disconnect()
       	await ctx.send("leave voice channel")
    except:
        	await ctx.send("The bot is not connected to a voice channel.")
    print("{}: Leave channel".format(ctx.message.author.name))

@bot.command(name='play', help='Bot plays song', aliases=["p"])
async def play(ctx, *, url):
    voice_client = ctx.voice_client
    if voice_client == None:
        await ctx.message.author.voice.channel.connect()
        voice_client = ctx.voice_client

    server = ctx.message.guild
    voice_channel = server.voice_client

    if voice_client.is_playing():
        voice_channel.stop()

    async with ctx.typing():
        file = await YTDLSource.from_url(url, loop=bot.loop)
        voice_channel.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio( source=file), 0.5))

    await ctx.send('**Jetzt läuft:** {}'.format(getTitle()))
    print("{}: Play song    ".format(ctx.message.author.name) + "Title: {}".format(getTitle()))
    await status()

async def status():
    global start
    start = time.time()
    status = discord.Activity(type=discord.ActivityType.listening, name=getTitle())
    await bot.change_presence(activity=status)
    await asyncio.sleep(getDuration())
    await bot.change_presence(activity=discord.Game('Discord'))
    await clear()

async def clear():
    try:
    	os.remove(getFilename())
    except:
    	return

@bot.command(name="stop", help="Stop playing song.")
async def stop(ctx):
    voice_channel = ctx.message.guild.voice_client
    await ctx.send("**stop**")
    voice_channel.stop()
    os.remove(getFilename())
    await bot.change_presence(activity=bot.guilds[0].get_member(bot.user.id).activity)
    await bot.change_presence(activity=discord.Game('Discord'))
    print("{}: Stop".format(ctx.message.author.name))

@bot.command(name="pause", help="pause playing song")
async def pause(ctx):
    #global end
    #pause = 1
    #end = time.time()
    #duration = 3600
    voice_client = ctx.message.guild.voice_client
    await ctx.send("**pause**")
    voice_client.pause()
    await bot.change_presence(activity=discord.Game('Discord'))
    print("{}: Pause".format(ctx.message.author.name))
    #await status()

@bot.command(name="resume", help="resume song")
async def resume(ctx):
    #pause = 0
    #duration = durations - (end-start)
    voice_client = ctx.message.guild.voice_client
    await ctx.send("**resume**")
    voice_client.resume()
    print("{}: Resume".format(ctx.message.author.name))
    #await status()

@bot.command(name="echo", help="echo")
async def echo(ctx, * , msg):
    await ctx.send(msg)
    print("{}: Echo     ".format(ctx.message.author.name) + "echo: ".join(msg))

@bot.command(name="fuck", help="Fuck you.")
async def fuck(ctx, * , msg):
    if msg == "you":
        await ctx.send('**Fuck you.**', tts=true)

    elif msg == "off":
        await ctx.send('Okay.')
    else:
        await ctx.send("Fuck " + msg)
    print("{}: Fuck ".format(ctx.message.author.name) + "".join(msg))

@bot.command(name="dm", help="Nachrichten per DM senden. Bsp.: ;dm @Nutzer @Nutzer1 eine Nachricht")
async def dm(ctx, users: commands.Greedy[discord.User], *, message):
    for user in users:
        await user.send("from {} : ".format(ctx.message.author.name) + message)
        print('{} send: "'.format(ctx.message.author.name) + message +'" to {}'.format(user))

@bot.command(name="getPrice", help="showing current stock market price.", aliases=["getP"])
async def getPrice(ctx, comp, number: int = 1):
    price = yf.Ticker(comp)
    price = price.info['regularMarketPrice']
    out = "Current price of "
    curr = "$"
    if "eur" in comp:
        curr = "€"
    if number != 1:
        out = "Total value of {} shares ".format(number)
    print("{}: getPrice     ".format(ctx.message.author.name) + "from: {}".format(comp) + "={}".format(price*number))
    await ctx.send(out + comp + ": {}".format(round(number *price,4)) + curr)

@bot.command(name="DOGE", help="show current DOGE Price.", aliases=["doge"])
async def doge(ctx, currency: str = "eur", number: float = 1):
    out = "Current price:"
    if currency == "usd" :
        price = yf.Ticker("DOGE-USD")
        doge = price.info['regularMarketPrice']
        curr = "$"
    else:
        price = yf.Ticker("DOGE-EUR")
        doge = price.info['regularMarketPrice']
        curr = "€"

    print("{}: DOGE         ".format(ctx.message.author.name) + "price/value: {}".format(number*doge))
    await ctx.send(out + " {}".format(round(number *doge,4)) + curr)

@bot.command(name="ping", help="Shows latency")
async def ping(ctx):
    await ctx.send("Mein Ping ist {} ms ".format(round(bot.latency * 1000)))
    print("{}: Ping         ".format(ctx.message.author.name) + "Ping: {}".format(round(bot.latency * 1000)))

async def say(msg):
    channel = bot.get_channel(756947903515197510)
    await channel.send(msg)

@bot.command(name = "twitch", help = "check if a stream is on" )
async def twitch(ctx, user):
    url= 'https://www.twitch.tv/' +user
    contents = requests.get(url).content.decode('utf-8')
    if 'isLiveBroadcast' in contents:
        await ctx.send(f"{user} ist live: \n{url}")
    else:
        await ctx.send(f"{user} scheint nicht live zu sein")

@bot.command(name = "pferdegeruch!")
async def pferd(ctx):
    voice_client = ctx.voice_client
    #await ctx.message.delete()
    if voice_client == None:
        await ctx.message.author.voice.channel.connect()
        voice_client = ctx.voice_client

    server = ctx.message.guild
    voice_channel = server.voice_client

    if voice_client.is_playing():
        voice_channel.stop()
    voice_channel.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio( source="sounds/Du-stinkst-nach-Pferd.mp3"), 2))

@bot.command(name="log")
async def log(ctx, file: str = "latest"):
    dir = "/home/quigon/minecraft/Fabric-1.17.1/logs/"
    if "latest" in file:
        await ctx.send(file=discord.File(r'{}latest.log'.format(dir)))
        print("log sent")

@bot.command(name="kill" , help="kill program")
async def kill(ctx):
    voice_client = ctx.message.guild.voice_client
    await ctx.send("shutting down the MegaBot")
    print("{}: Kill".format(ctx.message.author.name))
    try:
        await voice_client.disconnect()
        await bot.close()
        os._exit(0)
    except:
        await bot.close()
        os._exit(0)

bot.run(TOKEN)
