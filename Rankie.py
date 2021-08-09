import os
import sys
import atexit
import logging

from discord.ext import commands

from Channel_Management import channel_management
from Rank_Management import rank_management
from Administrator import administrator
from Database import rankie_db
from Config import config
from Events import events
from Tasks import tasks
from Help import help

#TODO: Change bot status once every 24 hrs to something funny

# Setup logging
if not os.path.exists('./logs'):
    os.mkdir('./logs')

if len(sys.argv) > 1 and 'DEBUG' in sys.argv[1].upper():
    logging.basicConfig(filename='./logs/rankie.log', filemode='w', level=logging.INFO, format='%(asctime)s: %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
else:
    logging.basicConfig(filename='./logs/rankie.log', filemode='w', level=logging.ERROR, format='%(asctime)s: %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Setup db
db = rankie_db()

# Setup config
cfg = config(logging, db)

# Setup Events
evts = events(logging, cfg, db)

# Setup rank_management
rnk_mng = rank_management(logging, cfg, db)

# Setup channel management
chnl_mng = channel_management(logging, cfg, db)

# Setup help
hlp = help(cfg)

# Create the bot
rankie = commands.Bot(command_prefix=cfg.get_prefix, help_command=None, case_insensitive=True)

# Setup admin
admin = administrator(rankie, logging)

# Setup tasks
tsks = tasks(rankie, logging, db)

#? BOT EVENTS

@rankie.event
async def on_ready():
    await evts.on_ready()

@rankie.event
async def on_command_error(ctx, error):
    await evts.on_command_error(ctx, error)

@rankie.event
async def on_guild_join(guild):
    await evts.on_guild_join(guild)

@rankie.event
async def on_guild_remove(guild):
    await evts.on_guild_remove(guild)

#? BOT COMMANDS

@rankie.command(name='assignRank', aliases=['ar'])
async def assign_rank(ctx, *cmd):
    await rnk_mng.assign_rank(ctx, cmd)

@rankie.command(name='profile', aliases=['p'])
async def profile(ctx, *cmd):
    await rnk_mng.profile(ctx, cmd)

@rankie.command(name='setRank', aliases=['sr'])
@commands.has_permissions(manage_guild=True)
async def set_rank(ctx, IO_range, *rank_name):
    await rnk_mng.set_rank(ctx, IO_range, rank_name)

@rankie.command(name='deleteRank', aliases=['dr'])
@commands.has_permissions(manage_guild=True)
async def delete_rank(ctx, *rank_name):
    await rnk_mng.delete_rank(ctx, rank_name)

@rankie.command(name='listRanks', aliases=['lr'])
async def list_ranks(ctx):
    await rnk_mng.list_ranks(ctx)

@rankie.command(name='setSeason', aliases=['ss'])
@commands.has_permissions(manage_guild=True)
async def set_season(ctx, desired_season):
    await rnk_mng.set_season(ctx, desired_season)

@rankie.command(name='setManagedChannel', aliases=['smc'])
@commands.has_permissions(manage_guild=True)
@commands.bot_has_guild_permissions(manage_messages=True)
async def set_managed_channel(ctx, channel_name, frequency):
    await chnl_mng.set_managed_channel(ctx, channel_name, frequency)

@rankie.command(name='deleteManagedChannel', aliases=['dmc'])
@commands.has_permissions(manage_guild=True)
async def delete_managed_channel(ctx, channel_name):
    await chnl_mng.delete_managed_channel(ctx, channel_name)

@rankie.command(name='setSavedMessage', aliases=['ssm'])
@commands.has_permissions(manage_guild=True)
async def set_saved_message(ctx, channel_name, message_id):
    await chnl_mng.set_saved_message(ctx, channel_name, message_id)

@rankie.command(name='deleteSavedMessage', aliases=['dsm'])
@commands.has_permissions(manage_guild=True)
async def delete_saved_message(ctx, channel_name, message_id):
    await chnl_mng.delete_saved_message(ctx, channel_name, message_id)

@rankie.command(name='listManagedChannels', aliases=['lmc'])
@commands.has_permissions(manage_guild=True)
async def list_managed_channels(ctx):
    await chnl_mng.list_managed_channels(ctx)

@rankie.command(name='listSavedMessages', aliases=['lsm'])
@commands.has_permissions(manage_guild=True)
async def list_managed_messages(ctx, channel_name):
    await chnl_mng.list_managed_messages(ctx, channel_name)

@rankie.command(name='setPrefix', aliases=['sp'])
@commands.has_permissions(manage_guild=True)
async def set_prefix(ctx, desired_prefix):
    await cfg.set_prefix(ctx, desired_prefix)

@rankie.command(name='help', aliases=['h'])
async def help(ctx, *cmd):
    await hlp.help_message(ctx, cmd)

#? Owner command only, allows the download of the config files
@rankie.command(name='getLogFile', aliases=['glf'])
@commands.is_owner()
async def get_config_file(ctx):
    await admin.get_log_file(ctx)

#? Owner command only, lists the servers Rankie is currently managing
@rankie.command(name='getGuilds', aliases=['gg'])
@commands.is_owner()
async def get_guilds(ctx):
    await admin.get_guilds(ctx)

# Setup repeated tasks
rankie.loop.create_task(tsks.channel_management())
rankie.loop.create_task(tsks.change_status())

@atexit.register
def on_exit():
    db.close_db()

# Run the bot!
if cfg.get_token() != None:
    rankie.run(cfg.get_token())
else:
    logging.error('Failed to find a discord token in the environment')
    print('Failed to find a discord token in the environment.')
