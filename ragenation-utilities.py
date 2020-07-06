import discord
from discord import TextChannel
from discord.ext import commands
import asyncio
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from ast import literal_eval
from urllib.request import urlopen

# Google Sheets Api Initializing
scope = [
    "https://spreadsheets.google.com/feeds",
    'https://www.googleapis.com/auth/spreadsheets',
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(keyfile_dict=literal_eval(node_or_string=urlopen(url=os.getenv('API_SHEETS_CERDSLINK')).read().decode()), scopes=scope) 
client = gspread.authorize(creds)
sheet = client.open("api_sheets_rn").sheet1

# Setting up the discord client
client = commands.Bot(command_prefix=('r!', '.', '!', '>', 'r/', '-', 'r-'), case_insensitive=True)
client_secret = os.getenv("API_DISCORD_BOTTOKEN")
client.remove_command('help')
client.id_user_zacky = 625987962781433867

def sync_channel_ids(client=client, sheet=sheet):
    client.id_channel_logs = int(sheet.cell(1, 1).value)
    client.id_channel_announcements = int(sheet.cell(2, 1).value)
    client.id_channel_polls = int(sheet.cell(3, 1).value)
    return int(sheet.cell(1, 1).value), int(sheet.cell(2, 1).value), int(sheet.cell(3, 1).value)

@client.event
async def on_ready():
    try:
        await client.get_channel(client.id_channel_logs).send("Bot has rebooted, rebooted successful")
    finally:
        print(sync_channel_ids())
    
@client.command(aliases=['setchannel'])
async def set_channel(ctx, channel_to_set_for, channel_to_set : discord.TextChannel):
    
    if channel_to_set_for.lower() in ('logs', 'botlogs', 'logschannel', 'botlogschannel', 'blotlogchannel', 'botlog', 'log', 'logchannel'):
        sheet.update_cell(1, 1, "'"+str(channel_to_set.id))
        await ctx.send("Done")
    elif channel_to_set_for.lower() in ('announcements', 'announcement', 'announcementschannel', 'announcementchannel'):
        sheet.update_cell(2, 1, "'"+str(channel_to_set.id))
        await ctx.send("Done")
    elif channel_to_set_for.lower() in ('polls', 'pollschannel', 'pollchannel', 'suggestionschannel', 'suggestions'):
        sheet.update_cell(3, 1, "'"+str(channel_to_set.id))
        await ctx.send("Done")
        
    sync_channel_ids()
                
@set_channel.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embde=discord.Embed(
            title="Missing Arguments",
            description="Please follow the following format for this command\n`.SetChannel [\"announcementsChannel\" or \"PollsChannel\" or \"BotLogsChannel\"] <TextChannel>`",
            color=discord.Color.red()
        ))
    elif isinstance(error, commands.ConversionError):
        await ctx.send(embed=discord.Embed(
            title="Type Error!",
            description="Please send the text channel and ONLY the text channel to set to",
            color=discord.Color.red()
        ))
    else:
        await client.get_user(client.id_user_zacky).send(error)

@client.command(aliases=["announce", "makeannouncement"])
async def make_an_announcement(ctx, *, to_announce):
    if client.get_channel(client.id_channel_announcements).permissions_for(ctx.author).send_messages:
        try: 
            title, description = to_announce.split(",")
        except Exception as e:
            await ctx.send(".announce This is a title, This is a description seperated by a comma there. only use one comma in your command")
            return
    
        try:
            await client.get_channel(client.id_channel_announcements).send(embed=discord.Embed(
                title=title,
                description=description,
                color=discord.Color.green()
            ))
        except:
            await ctx.send("Looks like I am missing some permissions or something")
    else:
        await ctx.send(f"You need the \"Send Message\" Permission in the channel that is currently labeled as the announcements channel (<#{client.id_channel_announcements}>)")
        
@client.command(aliases=["poll", "createpoll", "suggest"])
async def create_poll(ctx, to_poll):
    message = await client.get_channel(client.id_channel_polls).send(to_poll)
    await message.add_reaction("👍")
    await message.add_reaction("👎")
    
@client.command(aliases=['status', 'serverstatus', 'members'])
async def count_members(ctx):
    client.minecraft_server_stats = literal_eval(node_or_string=urlopen(url="https://api.mcsrvstat.us/2/play.ragenation.tk").read().decode().replace('false', 'False').replace('true', 'True'))
    client.minecraft_server_members_count = client.minecraft_server_stats['players']['online']
    
    await ctx.send(embed=discord.Embed(
        title="Minecraft Server online",
        description=f"**{client.minecraft_server_members_count}** Number of members online!",
        color=discord.Color.blue()
    ).set_footer(
        text="this status message will be refined and detailed soon, in a day or two"
    ))
    
@client.command()
async def help(ctx):
    await ctx.send(embed=discord.Embed(
        title="Ragenation | Utilities Commands",
        description="`.suggest <ToSuggest>` : Suggest something, anything\n`.announce <ToAnnounce>` : Announce something in this server\n`.help` : yes\n`.serverStatus` : Status of the minecraft server\n`.SetChannel [\"announcementsChannel\" or \"PollsChannel\" or \"BotLogsChannel\"] <TextChannelToSet>` : This is for telling me which channel is for what",
        color=discord.Color.from_rgb(0, 0, 25)
    ).set_thumbnail(
        url="https://cdn.discordapp.com/icons/724544421416140801/f79ad4304fc0ff464be8170f757cc0e7.webp"
    ).set_footer(
        text="For support, please contact Zacky#9543"
    ))
    
client.run(client_secret)
