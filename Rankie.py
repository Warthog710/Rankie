import os
import logging

from discord.ext import commands

from Channel_Management import channel_management
from Rank_Management import rank_management
from Config import config
from Events import events
from Tasks import tasks
from Help import help

#TODO: Change bot status once every 24 hrs to something funny
#TODO: Change list messages to embeds (and help command)
#TODO: Improve assignRank response (make a pretty embed)

# Setup logging
if not os.path.exists('./logs'):
    os.mkdir('./logs')

logging.basicConfig(filename='./logs/rankie.log', level = logging.INFO, format='%(asctime)s: %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Setup config
cfg = config(logging)

# Setup Events
evts = events(logging, cfg)

# Setup rank_management
rnk_mng = rank_management(logging, cfg)

# Setup channel management
chnl_mng = channel_management(logging, cfg)

# Setup help
hlp = help(cfg)

# Create the bot
rankie = commands.Bot(command_prefix=cfg.get_prefix, help_command=None, case_insensitive=True)

# Setup tasks
tsks = tasks(rankie, logging, cfg)

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

# Setup repeated tasks
rankie.loop.create_task(tsks.hourly_management())
rankie.loop.create_task(tsks.daily_management())
rankie.loop.create_task(tsks.change_status())

# Run the bot!
rankie.run(cfg.config['discordToken'])
