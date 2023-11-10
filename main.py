# -- coding: utf-8 --

import discord
from discord.ext import commands
import environ
import requests
from bs4 import BeautifulSoup
import string

from emoji_dict import TYPE_EMOJI

#Чтение .env
env = environ.Env()
environ.Env.read_env()

URL_LOPUNNY = '/pokedex-sm/428.shtml'
URL_START = 'https://www.serebii.net'

HEADERS = {
    "Access": '*/*',
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

sl = list(string.ascii_lowercase)

#Запуск комманд бота
bot = commands.Bot(intents=discord.Intents.all(), command_prefix=env('BOT_PREFIX'), status=discord.Status.idle)

@bot.event
async def on_ready():
    pass

@bot.command(pass_context=True)
async def parse(ctx, pokemon):
    pokemon = pokemon.lower()

    if pokemon == 'lopunny':
        url = URL_START + URL_LOPUNNY
    else:
        url = None
        if sl.index(pokemon[0]) < 7:
            formname = 'cent'
        elif sl.index(pokemon[0]) >= 7 and sl.index(pokemon[0]) < 18:
            formname = 'coast'
        else:
            formname = 'mount'

        req = requests.get(URL_START + URL_LOPUNNY, headers=HEADERS)
        soup = BeautifulSoup(req.content, "lxml")
        selection = soup.find("form", {"name": formname}).find("select").findAll("option")
        for option in selection:
            if option.text.lower() == pokemon:
                url = URL_START + option['value']

    if url:
        req = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(req.content, "lxml")
        parsed = soup.findAll("table", {"class": 'dextable'})
        selection = parsed[1].findAll("td", {"class": ['fooinfo', 'cen']})

        if "is Genderless" in selection[-7].text:
            gender = "Genderless"
        else:
            gd = selection[-7].findAll("td")
            gender = f"{gd[1].text} Male. \n {gd[3].text} Female."

        types = ""
        for type in selection[-6].findAll("img"):
            types += f'{TYPE_EMOJI[type["alt"]]}  '

        locs = "-"
        for table in [parsed[6], parsed[7]]:
            if table.find("td", {"class": 'fooevo'}).text[0] == 'L':
                locs = table.findAll("td", {"class": 'fooinfo'})[3].text

        data = {
            "name": selection[0].text,
            "height": selection[-4].text.split("\r\n\t\t\t")[1],
            "weight": selection[-3].text.split("\r\n\t\t\t")[1],
            "class": selection[-5].text,
            "gender": gender,
            "type": types,
            "url": URL_START + soup.find("aside", {"id": 'rbar'}).find("img")["src"],
            "location": locs
        }

        embed = discord.Embed(title=f'Найден покемон {data["name"]}\n',
                              url=url,
                              description=f'Покемон класса {data["class"]}',
                              color=0xeada9d)
        embed.add_field(name='Параметры',
                        value=f'Пол: {data["gender"]}\n'
                        f'Тип: {data["type"]}\n'
                        f'Рост: {data["height"]}\n'
                        f'Вес: {data["weight"]}\n',
                        inline=False)
        embed.add_field(name='Локации',
                        value=f'{data["location"]}\n',
                        inline=False)
        embed.set_thumbnail(url=data["url"])
        await ctx.send(embed=embed)
    else:
        await ctx.send('Не нашла :(')

#Запуск бота
TOKEN = env('BOT_TOKEN')
bot.run(TOKEN)