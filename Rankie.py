import os
import json
import discord
import aiohttp
import asyncio
import logging

from discord.ext import commands
from datetime import datetime, timedelta

#TODO: Change bot status once every 24 hrs to something funny

#? Permissions required: manage_roles, 

#? Default prefix for Rankie
DEFAULT_PREFIX = '?'

#? The top cap for scores. Lets hope a mythic+ score can never be greater than 99999
INFINITY = 99999

# Setup logging
if not os.path.exists('./logs'):
    os.mkdir('./logs')

logging.basicConfig(filename='./logs/rankie.log', level = logging.INFO, format='%(asctime)s: %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Make sure the folder exists
if not os.path.exists('./config'):
    os.mkdir('./config')    

# Load config
try:
    with open('./config/config.json', 'r') as config:
        config = json.loads(config.read())
except Exception as e:
    logging.error(f'./config/config.json was not found: {e}')
    config = {}

# Load prefixes
try:
    with open('./config/prefixes.json', 'r') as prefixes:
        prefixes = json.loads(prefixes.read())
except Exception as e:
    logging.warning(f'./config/prefixes.json was not found! prefixes will be set to an empty dictionary: {e}')
    prefixes = {}

# Load roles
try:
    with open('./config/roles.json', 'r') as roles:
        roles = json.loads(roles.read())
except Exception as e:
    logging.warning(f'./config/roles.json was not found! roles will be set to an empty dictionary: {e}')
    roles = {}

# Load season
try:
    with open('./config/season.json', 'r') as season:
        season = json.loads(season.read())
except Exception as e:
    logging.warning(f'./config/season.json was not found! season will be set to an empty dictionary: {e}')
    season = {}

# Load managed guilds
try:
    with open('./config/managed_guilds.json', 'r') as managed_guilds:
        managed_guilds = json.loads(managed_guilds.read())
except Exception as e:
    logging.warning(f'./config/managed_guilds.json was not found! managed_guilds will be set to an empty dictionary: {e}')
    managed_guilds = {}

# Load managed channels
try:
    with open('./config/managed_channels.json', 'r') as managed_channels:
        managed_channels = json.loads(managed_channels.read())
except Exception as e:
    logging.warning(f'./config/managed_channels.json was not found! managed_channels will be set to an empty dictionary: {e}')
    managed_channels = {}

#? CUSTOM FUNCTIONS

def get_prefix(client, message):
    if str(message.guild.id) in prefixes:
        return prefixes[str(message.guild.id)]
    else:
        prefixes[str(message.guild.id)] = DEFAULT_PREFIX

        # Dump the new prefix into the JSON
        with open('./config/prefixes.json', 'w') as temp:
            json.dump(prefixes, temp, indent=4)

        # Return the default prefix
        return DEFAULT_PREFIX

def parse_cmd(cmd):
    region, realm, name = cmd[0].split('/')
    return region, realm, name

# Determines if an IO range is valid
def check_IO_range(IO_range):
    # The string contains a +
    if '+' in IO_range:
        temp = IO_range.split('+')[0]
        
        # If it is numeric
        if temp.isnumeric():
            if int(temp) >= 0:
                return True

    # The string contains a -
    elif '-' in IO_range:
        temp_min, temp_max = IO_range.split('-')

        if temp_max.isnumeric() and temp_min.isnumeric():
            if int(temp_min) >= 0:
                if int(temp_min) < int(temp_max):
                    return True

    return False

# Given an IO range string, parse it.
def parse_IO_range(IO_range):
    if '+' in IO_range:
        temp = int(IO_range.split('+')[0])
        return range(temp, INFINITY)

    elif '-' in IO_range:
        temp_min, temp_max = IO_range.split('-')
        return range(int(temp_min), int(temp_max))

# Determine if a valid IO range overlaps with an existing range
def detect_overlap(guild_id, IO_range, rank):
    # If roles exist for this guild
    if str(guild_id) in roles:
        existing_roles = roles[str(guild_id)]
        IO_range = parse_IO_range(IO_range)

        # Determine if a name overlaps
        if rank != None:
            for role in existing_roles:
                if role[0] == rank.id:
                    return False

        # Determine if a range overlaps
        for role in existing_roles:
            saved_range = parse_IO_range(role[1])
            if max(IO_range) >= min(saved_range) and max(saved_range) >= min(IO_range):
                return False

        # If no overlap was detected, the range is good.
        return True

    # Else, no roles exist for this guild, no overlap can occur
    else:
        return True

# Function defined to sort rank list
def sort_key(my_tuple):
    return min(parse_IO_range(my_tuple[1]))

# Given a guild id, return a sorted list of ranks
def get_sorted_ranks(guild_id):
    if str(guild_id) in roles:
        existing_roles = roles[str(guild_id)]
        existing_roles.sort(key=sort_key)
        return existing_roles
    # Return none if no roles exist for that server
    else:
        return None

# Given a guild id, return its season setting (previous or current)
def get_season(guild_id):
    if str(guild_id) in season:
        return season[str(guild_id)]
    else:
        season[str(guild_id)] = 'current'

        # Dump season to disk
        with open('./config/season.json', 'w') as temp:
            json.dump(season, temp, indent=4)

        return 'current' 

async def purge_channel(channel_id, reserved_messages):
    # Attempt to fetch channel
    try:
        channel = await rankie.fetch_channel(channel_id)
    except Exception as e:
        logging.info(f'Failed to fetch managed channel {channel_id}: {e}')
        return

    # Attempt to delete the messsages
    try:
        async for message in channel.history():
            if message.id in reserved_messages:
                continue
            else:
                await message.delete()

                # Discord rate limits you while deleting messages in this fashion. Sleeping for 1 second between deletions seems to resolve this
                await asyncio.sleep(1)
    except Exception as e:
        logging.info(f'Failed to delete messages in managed channel {channel_id}: {e}')
        await channel.send('Rankie attempted to manage this channel but failed. This is likely due to missing permissions. Please make sure Rankie has permission to __manage messages__ and __read message history__.')



async def add_role(ctx, role, IO_range):
    # Add the role
    if str(ctx.guild.id) in roles:
        roles[str(ctx.guild.id)].append((role.id, IO_range))
    else:
        roles[str(ctx.guild.id)] = [(role.id, IO_range)]

    # Dump roles to disk
    with open('./config/roles.json', 'w') as temp:
        json.dump(roles, temp, indent=4)

    await ctx.message.reply(f'Successfully created the rank {role} with an assigned IO range of {IO_range}.')

async def raider_io_query(ctx, region, realm, name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://raider.io/api/v1/characters/profile?region={region}&realm={realm}&name={name}&fields=mythic_plus_scores_by_season%3A{get_season(ctx.guild.id)}') as response:
            if response.status == 200:
                resp_json = await response.json()
                return resp_json
            elif response.status == 400:
                await ctx.message.reply(f'The character {region}/{realm}/{name} was not found. Please make sure that character exists.')
                return None
            else:
                await ctx.message.reply(f'Raider.io failed to respond. Please try again later.')
                return None

# Create the bot
rankie = commands.Bot(command_prefix=get_prefix, help_command=None, case_insensitive=True)

#? BOT TASKS

async def hourly_management():
    await rankie.wait_until_ready()

    # Sleep until the next hour
    next_hour = (datetime.now() + timedelta(hours=1)).replace(microsecond=0, second=0, minute=0)
    wait_seconds = (next_hour - datetime.now()).seconds
    await asyncio.sleep(wait_seconds)

    while not rankie.is_closed():
        for guild_id in managed_guilds:
            for channel_id in managed_guilds[str(guild_id)]:

                # Do the thing
                if managed_channels[str(channel_id)][0] == 'hourly':
                    await purge_channel(channel_id, managed_channels[str(channel_id)][1])

        # Sleep until the next hour
        next_hour = (datetime.now() + timedelta(hours=1)).replace(microsecond=0, second=0, minute=0)
        wait_seconds = (next_hour - datetime.now()).seconds
        await asyncio.sleep(wait_seconds)

async def daily_management():
    await rankie.wait_until_ready()

    # Sleep until the next day
    next_day = (datetime.now() + timedelta(days=1)).replace(microsecond=0, second=0, minute=0, hour=0)
    wait_seconds = (next_day - datetime.now()).seconds
    await asyncio.sleep(wait_seconds)

    while not rankie.is_closed():
        for guild_id in managed_guilds:
            for channel_id in managed_guilds[str(guild_id)]:

                # Do the thing
                if managed_channels[str(channel_id)][0] == 'daily':
                    await purge_channel(channel_id, managed_channels[str(channel_id)][1])

        # Sleep until the next day
        next_day = (datetime.now() + timedelta(days=1)).replace(microsecond=0, second=0, minute=0, hour=0)
        wait_seconds = (next_day - datetime.now()).seconds
        await asyncio.sleep(wait_seconds)

#? BOT EVENTS

@rankie.event
async def on_ready():
    logging.info('Rankie successfully started!')
    print('Rankie Successfully Started!')

@rankie.event
async def on_command_error(ctx, error):
    logging.info(f'Unspecified command error occurred: {error}')
    await ctx.message.reply(f'I didn\'t recognize that command. Try asking me **{get_prefix(None, ctx.message)}help**')

@rankie.event
async def on_guild_join(guild):
    logging.info(f'Rankie joined {guild.id}')
    prefixes[str(guild.id)] = DEFAULT_PREFIX

    # Dump the new prefix into the JSON
    with open('./config/prefixes.json', 'w') as temp:
        json.dump(prefixes, temp, indent=4)

@rankie.event
async def on_guild_remove(guild):
    logging.info(f'Rankie left {guild.id}')

    # Clean up prefixes
    if str(guild.id) in prefixes:
        del prefixes[str(guild.id)]

        # Dump the new prefix into the JSON
        with open('./config/prefixes.json', 'w') as temp:
            json.dump(prefixes, temp, indent=4)

    # Clean up roles
    if str(guild.id) in roles:
        del roles[str(guild.id)]

        # Dump the new prefix into the JSON
        with open('./config/roles.json', 'w') as temp:
            json.dump(roles, temp, indent=4)

    # Clean up season
    if str(guild.id) in season:
        del season[str(guild.id)]

        # Dump the new prefix into the JSON
        with open('./config/season.json', 'w') as temp:
            json.dump(season, temp, indent=4)

    # Clean up managed_channels
    if str(guild.id) in managed_guilds:
        temp = managed_guilds[str(guild.id)]
        del managed_guilds[str(guild.id)]

        for channel_id in temp:
            if str(channel_id) in managed_channels:
                del managed_channels[str(channel_id)]

#? BOT COMMANDS

@rankie.command(name='assignRank', aliases=['ar'])
async def assign_rank(ctx, *cmd):
    try:
        region, realm, name = parse_cmd(cmd)
        resp_json = await raider_io_query(ctx, region, realm, name)

        # If none is returned, the character was not found, or the API is down.
        if resp_json == None:
            return
        # Else, grab the current score
        else:
            mythic_score = resp_json['mythic_plus_scores_by_season'][0]['scores']['all']

    except Exception as e:
        logging.info(f'Failed to recognize the command for assignRank. Cmd={cmd}: {e}')
        await ctx.message.reply(f'I didn\'t recognize that command. Try asking me: **{get_prefix(None, ctx.message)}help assignRank**')
        return

    # Get a sorted list of ranks
    sorted_ranks = get_sorted_ranks(ctx.guild.id)

    # If no ranks exist
    if sorted_ranks == None:
        await ctx.message.reply('No ranks currently exist on this server. Please create some ranks.')
        return

    # Determine if they qualify for a rank
    rank_id = None
    for item in sorted_ranks:
        if int(mythic_score) in parse_IO_range(item[1]):
            rank_id = item[0]
            break

    # If rank_id is none, they don't qualify for anything
    if rank_id == None:
        await ctx.message.reply('You do not currently qualify for any set ranks.')
        return

    # Check if the user currently posseses that rank
    if discord.utils.get(ctx.message.author.roles, id=rank_id) != None:
        await ctx.message.reply('You already possess the correct rank.')
        return

    try:
        # Remove all current managed ranks from the user
        for item in sorted_ranks:
            temp = discord.utils.get(ctx.message.author.roles, id=item[0])

            if temp != None:
                await ctx.message.author.remove_roles(discord.utils.get(ctx.message.guild.roles, id=item[0]))

        # Add new rank
        await ctx.message.author.add_roles(discord.utils.get(ctx.message.guild.roles, id=rank_id))
    except Exception as e:
        await ctx.message.reply('Failed to assign the correct rank. This is likely due to a permissions issue. Please make sure Rankie has the ability to assign and delete roles.')
        logging.warning(f'Failed to delete/assign a new role: {e}')
        return    

    await ctx.message.reply(f'You have been assigned {discord.utils.get(ctx.message.guild.roles, id=rank_id)}. This rank is for players with a mythic+ score of {dict(sorted_ranks)[rank_id]}.')     

@rankie.command(name='profile', aliases=['p'])
async def profile(ctx, *cmd):
    try:
        region, realm, name = parse_cmd(cmd)
        resp_json = await raider_io_query(ctx, region, realm, name)

        # if none is returned, the character was not found, or the API is down.
        if resp_json == None:
            return
        else:
            profile_url = resp_json['profile_url']
    except Exception as e:
        logging.info(f'Failed to recognize the command for profile. Cmd={cmd}: {e}')
        await ctx.message.reply(f'I didn\'t recognize that command. Try asking me: **{get_prefix(None, ctx.message)}help profile**')
        return

    await ctx.message.reply(profile_url)

@rankie.command(name='setRank', aliases=['sr'])
@commands.has_permissions(manage_guild=True)
async def set_rank(ctx, IO_range, *rank_name):
    rank_name = ' '.join(rank_name)

    # If the rank_name is nothing, return an error
    if len(rank_name) <= 0:
        await ctx.message.reply(f'The name for the rank must be greater than 0 characters.')
        return

    rank = discord.utils.get(ctx.message.guild.roles, name=rank_name)

    # Verify IO_range
    try:
        # Determine if a valid range was sent
        if not check_IO_range(IO_range):
            await ctx.message.reply(f'The IO range {IO_range} is invalid.')
            return

        # Verify the passed IO range does not overlap with an existing saved range
        if not detect_overlap(ctx.guild.id, IO_range, rank):
            await ctx.message.reply(f'The rank or IO range passed already exists.')
            return
    except Exception as e:
        logging.info(f'Failed to recognize the command for add_role. role={rank} IO_range={IO_range}: {e}')
        await ctx.message.reply(f'I didn\'t recognize that command. Try asking me: **{get_prefix(None, ctx.message)}help setRank**')
        return

    # If check for dupe is false, the role does not exist
    if rank == None:
        # Attemp to create the role
        try:
            rank = await ctx.guild.create_role(name=rank_name)
        except Exception as e:
            logging.warning(f'Failed to create a new rank in setRank: {e}')
            await ctx.message.reply('Failed to create the requested rank. This is likely due to a permissions issue. Please make sure Rankie has the ability to create roles or manually create the role before setting the rank.')
            return

    # Add the role
    await add_role(ctx, rank, IO_range)

@rankie.command(name='deleteRank', aliases=['dr'])
@commands.has_permissions(manage_guild=True)
async def delete_rank(ctx, *rank_name):
    rank_name = ' '.join(rank_name)

    # If the guild ID does not exist in roles, no ranks can be deleted since none have been sent
    if not str(ctx.guild.id) in roles:
        await ctx.message.reply(f'No ranks exist for this server. Before deleting a rank you must create it.')
        return

    # If the role ID does not exist on the server
    rank = discord.utils.get(ctx.message.guild.roles, name=rank_name)
    if rank == None:
        await ctx.message.reply(f'I could not find the passed rank on this server. Please verify the rank exists.')
        return

    # Delete the rank
    roles[str(ctx.guild.id)] = [x for x in roles[str(ctx.guild.id)] if x[0] != rank.id]
    
    # Dump roles to disk
    with open('./config/roles.json', 'w') as temp:
        json.dump(roles, temp, indent=4)

    # Attempt to delete the rank from the server
    try:
        await rank.delete()
    except Exception as e:
        logging.warning(f'Failed to delete a rank in deleteRank: {e}')
        await ctx.message.reply(f'Successfully deleted the rank {rank_name} internally. However, failed to delete the role on the server. This is likely a permissions issue. Please make sure Rankie has the ability to delete roles or manually delete the role.')
        return

    await ctx.message.reply(f'Successfully deleted the rank {rank_name}.')

@rankie.command(name='listRanks', aliases=['lr'])
async def list_ranks(ctx):
    sorted_ranks = get_sorted_ranks(ctx.guild.id)
    if sorted_ranks != None:
        if len(sorted_ranks) > 0:
            msg = f'Currently set ranks:\n```{"Rank Name":<20}\t{"IO Range":<20}\n'
            msg += f'{"---------":<20}\t{"--------":<20}\n'

            for item in sorted_ranks:
                rank_name = str(discord.utils.get(ctx.message.guild.roles, id=item[0]))
                msg += f'{rank_name:<20}\t{item[1]:<20}\n'

            msg += '```'
            await ctx.message.reply(msg)
            return

    await ctx.message.reply(f'I could not find any set ranks for this server. Please try setting a rank before using this command.')
    logging.info(f'Failed to find any roles in listRanks for guild {ctx.guild.id}')

@rankie.command(name='setPrefix', aliases=['sp'])
@commands.has_permissions(manage_guild=True)
async def set_prefix(ctx, desired_prefix):
    # Accept only prefixes of a single char
    if len(desired_prefix) == 1:
        prefixes[str(ctx.guild.id)] = desired_prefix

        # Dump the new prefix
        with open('./config/prefixes.json', 'w') as temp:
            json.dump(prefixes, temp, indent=4)

        # Inform the change
        await ctx.message.reply(f'Prefix successfully changed to: **{desired_prefix}**')

    # An invalid prefix was sent
    else:
        await ctx.message.reply(f'Desired prefix was invalid. Prefix must be a single character.')

@rankie.command(name='setSeason', aliases=['ss'])
@commands.has_permissions(manage_guild=True)
async def set_season(ctx, desired_season):
    desired_season = str(desired_season).lower()

    if desired_season == 'current':
        season[str(ctx.guild.id)] = 'current'
        
        # Dump the new prefix into the JSON
        with open('./config/season.json', 'w') as temp:
            json.dump(season, temp, indent=4)

        await ctx.message.reply('The __current__ season will now be used for scores.')

    elif desired_season == 'previous':
        season[str(ctx.guild.id)] = 'previous'

        # Dump the new prefix into the JSON
        with open('./config/season.json', 'w') as temp:
            json.dump(season, temp, indent=4)

        await ctx.message.reply('The __previous__ season will now be used for scores.')

    else:
        await ctx.message.reply(f'I didn\'t recognize that command. Try asking me: **{get_prefix(None, ctx.message)}help setSeason**')

@rankie.command(name='setManagedChannel', aliases=['smc'])
@commands.has_permissions(manage_guild=True)
@commands.bot_has_guild_permissions(manage_messages=True)
async def set_managed_channel(ctx, channel_name, frequency):
    channel = discord.utils.get(ctx.message.guild.channels, name=channel_name)

    # If channel_name is none it does not exist
    if channel == None:
        await ctx.message.reply(f'I couldn\'t find a channel with the name __{channel_name}__.')
        return

    # Only allow text channels
    if str(channel.type) == 'voice' or str(channel.type) == 'store' or str(channel.type) == 'stage_voice':
        await ctx.message.reply(f'Only text channels can be managed.')
        return

    # If frequency is not hourly or daily throw an error
    frequency = frequency.lower()
    if frequency != 'hourly' and frequency != 'daily':
        await ctx.message.reply('Received an invalid frequency. Only __daily__ and __hourly__ are accepted.')
        return

    # Set the managed channel if it does not exist
    if str(channel.id) in managed_channels:
        await ctx.message.reply(f'The channel __{channel_name}__ is already managed.')
    else:
        managed_channels[str(channel.id)] = [frequency, []]

        if str(ctx.guild.id) in managed_guilds:
            managed_guilds[str(ctx.guild.id)].append(channel.id)
        else:
            managed_guilds[str(ctx.guild.id)] = [channel.id]

        # Dump managed_channels and managed_guilds to disk
        with open('./config/managed_channels.json', 'w') as temp:
            json.dump(managed_channels, temp, indent=4)

        with open('./config/managed_guilds.json', 'w') as temp:
            json.dump(managed_guilds, temp, indent=4)

        await ctx.message.reply(f'The channel __{channel_name}__ is now being managed by Rankie on a __{frequency}__ basis.')

@rankie.command(name='deleteManagedChannel', aliases=['dmc'])
@commands.has_permissions(manage_guild=True)
async def delete_managed_channel(ctx, channel_name):
    channel = discord.utils.get(ctx.message.guild.channels, name=channel_name)

    # If channel is none it does not exist
    if channel == None:
        await ctx.message.reply(f'I couldn\'t find a channel with the name __{channel_name}__.')
        return

    # Delete the managed channel from managed channels
    if str(channel.id) in managed_channels:
        del managed_channels[str(channel.id)]
    else:
        await ctx.message.reply(f'The channel __{channel_name}__ is already not managed by Rankie.')
        return

    # Delete the channel from the managed guild list
    if str(ctx.guild.id) in managed_guilds:
        managed_guilds[str(ctx.guild.id)].remove(channel.id)

        # If no more entries exist for that guild, remove it.
        if len(managed_guilds[str(ctx.guild.id)]) <= 0:
            del managed_guilds[str(ctx.guild.id)]

    # Dump managed_channels and managed_guilds to disk
    with open('./config/managed_channels.json', 'w') as temp:
        json.dump(managed_channels, temp, indent=4)

    with open('./config/managed_guilds.json', 'w') as temp:
        json.dump(managed_guilds, temp, indent=4)

    await ctx.message.reply(f'The channel __{channel_name}__ will no longer be managed by Rankie.')

@rankie.command(name='setSavedMessage', aliases=['ssm'])
@commands.has_permissions(manage_guild=True)
async def set_saved_message(ctx, channel_name, message_id):
    channel = discord.utils.get(ctx.message.guild.channels, name=channel_name)

    # If channel is none it does not exist
    if channel == None:
        await ctx.message.reply(f'I couldn\'t find a channel with the name __{channel_name}__.')
        return

    # If the passed id is not numeric, then its not a valid id
    if not message_id.isnumeric():
        await ctx.message.reply(f'The ID {message_id} is not valid.')
        return

    try:
        msg = await channel.fetch_message(int(message_id))
    except Exception as e:
        logging.info(f'Failed to find a message in {channel_name}. message_id={message_id}: {e}')
        await ctx.message.reply(f'Failed to find a message in __{channel_name}__ associated with the passed ID __{message_id}__')
        return

    # Verify that Rankie is currently managing that channel
    if str(channel.id) in managed_channels:

        # If the message is already managed, throw an error
        if msg.id in managed_channels[str(channel.id)][1]:
            await ctx.message.reply(f'The message __{msg.id}__ is already being saved by Rankie.')
        else:
            managed_channels[str(channel.id)][1].append(msg.id)

            # Dump managed_channel to disk
            with open('./config/managed_channels.json', 'w') as temp:
                json.dump(managed_channels, temp, indent=4)

            await ctx.message.reply(f'The message __{msg.id}__ in __{channel_name}__ will now be saved by Rankie.')

    # Else, the channel is not currently managed...
    else:
        await ctx.message.reply(f'The channel {channel_name} is not currently managed by Rankie, please ask Rankie to manage this channel before setting any saved message(s).')

@rankie.command(name='deleteSavedMessage', aliases=['dsm'])
@commands.has_permissions(manage_guild=True)
async def delete_saved_message(ctx, channel_name, message_id):
    channel = discord.utils.get(ctx.message.guild.channels, name=channel_name)

    # If channel is none it does not exist
    if channel == None:
        await ctx.message.reply(f'I couldn\'t find a channel with the name __{channel_name}__.')
        return

    # If the passed id is not numeric, then its not a valid id
    if not message_id.isnumeric():
        await ctx.message.reply(f'The ID {message_id} is not valid.')
        return

    # Verify the channel is being managed by Rankie
    if str(channel.id) in managed_channels:

        # If the message is being saved
        if int(message_id) in managed_channels[str(channel.id)][1]:
            managed_channels[str(channel.id)][1].remove(int(message_id))

            # Dump managed_channels to disk
            with open('./config/managed_channels.json', 'w') as temp:
                json.dump(managed_channels, temp, indent=4)

            await ctx.message.reply(f'The message __{message_id}__ will NO longer be saved by Rankie.')
        
        else:
            await ctx.message.reply(f'The message __{message_id}__ is already not being saved or the passed message ID is invalid.')
    else:
        await ctx.message.reply(f'The channel __{channel_name}__ is not currently managed by Rankie, please ask Rankie to manage this channel before deleting any saved message(s).')

@rankie.command(name='listManagedChannels', aliases=['lmc'])
@commands.has_permissions(manage_guild=True)
async def list_managed_channels(ctx):

    # Check if the guild has managed channels
    if str(ctx.guild.id) in managed_guilds:
        msg = f'Managed channels:\n```{"Channel":<20}\t{"Frequency":<20}\n{"-------":<20}\t{"---------":<20}\n'

        for channel_id in managed_guilds[str(ctx.guild.id)]:
            channel_name = str(discord.utils.get(ctx.message.guild.channels, id=channel_id))
            msg += f'{channel_name:<20}\t{managed_channels[str(channel_id)][0]:<10}\n'

        msg += '```'
        await ctx.message.reply(msg)
    else:
        await ctx.message.reply(f'This server has no currently managed channels. Please ask **{get_prefix(None, ctx.message)}help setManagedChannel** to learn how to set them.')

@rankie.command(name='listSavedMessages', aliases=['lsm'])
@commands.has_permissions(manage_guild=True)
async def list_managed_messages(ctx, channel_name):
    channel = discord.utils.get(ctx.message.guild.channels, name=channel_name)

    # If channel is none it does not exist
    if channel == None:
        await ctx.message.reply(f'I couldn\'t find a channel with the name __{channel_name}__.')
        return

    # If the channel is being managed
    if str(channel.id) in managed_channels:
        # If the length of saved messages is > 0
        if len(managed_channels[str(channel.id)][1]) > 0:
            msg = f'Saved message(s) in __{channel_name}__:\n'
            for msg_id in managed_channels[str(channel.id)][1]:
                msg += f'``{msg_id}``\n'

            await ctx.message.reply(msg)
        else:
            await ctx.message.reply(f'The channel __{channel_name}__ has no saved messages.')
    else:
        await ctx.message.reply(f'The channel __{channel_name}__ is not currently being managed by Rankie.')

@rankie.command(name='help', aliases=['h'])
async def help(ctx, *cmd):
    prefix = get_prefix(None, ctx.message)
    cmd = ' '.join(cmd)
    cmd = cmd.upper()

    if 'ASSIGNRANK' == cmd or 'AR' == cmd:
        msg = f'```Assigns a rank based on your current Raider.io mythic+ score.\n\nUsage: {prefix}assignRank <region>/<realm>/<name>\n\nAliases: {prefix}ar\n\nExample: {prefix}assignRank us/aggramar/sapphirre```'
        await ctx.message.reply(msg)
    elif 'PROFILE' == cmd or 'P' == cmd:
        msg = f'```Return the URL for a characters Raider.io profile.\n\nUsage: {prefix}profile <region>/<realm>/<name>\n\nAliases: {prefix}p\n\nExample: {prefix}profile us/aggramar/sapphirre```'
        await ctx.message.reply(msg)
    elif 'LISTRANKS' == cmd or 'LR' == cmd:
        msg = f'```Lists all the currently set ranks for this server.\n\nUsage: {prefix}listRanks\n\nAliases: {prefix}lr```'
        await ctx.message.reply(msg)
    elif ('SETRANK' == cmd or 'SR' == cmd) and ctx.message.author.guild_permissions.manage_guild:
        msg = f'```Adds a rank attached to a specified IO range. When a member asks to be assigned a rank and their mythic+ score is within this range, the associated rank will be assigned.\n\nUsage: {prefix}setRank <IO_Range> [Rank Name]\n\nAliases: {prefix}sr\n\nExample: {prefix}setRank 0-1000 Baby\nExample: {prefix}setRank 1000+ Bigger Baby\n\nNote, the IO range passed or the rank name cannot overlap with existing managed ranks. In addition, the end value of a range is exclusive. This means that the range 0-1000 maxes out at 999.```'
        await ctx.message.reply(msg)
    elif ('DELETERANK' == cmd or 'DR' == cmd) and ctx.message.author.guild_permissions.manage_guild:
        msg = f'```Deletes a rank that already exists.\n\nUsage: {prefix}deleteRank [Rank Name]\n\nAliases: {prefix}dr\n\nExample: {prefix}deleteRank Bigger Baby```'
        await ctx.message.reply(msg)
    elif ('SETPREFIX' == cmd or 'SP' == cmd) and ctx.message.author.guild_permissions.manage_guild:
        msg = f'```Sets the prefix that Rankie uses for this server.\n\nUsage: {prefix}setPrefix <desired_prefix>\n\nAliases: {prefix}sp\n\nExample: {prefix}setPrefix !```'
        await ctx.message.reply(msg)
    elif ('SETSEASON' == cmd or 'SS' == cmd) and ctx.message.author.guild_permissions.manage_guild:
        msg = f'```Sets the current season that will be used to assign ranks.\n\nUsage: {prefix}setSeason <desired_season>\n\nAliases: {prefix}ss\n\nOnly "current" and "previous" are supported as inputs for this command.```'
        await ctx.message.reply(msg)
    elif ('SETMANAGEDCHANNEL' == cmd or 'SMC' == cmd) and ctx.message.author.guild_permissions.manage_guild:
        msg = f'```Sets a channel to be managed. A managed channel will have its messages periodically deleted at a defined frequency. Currently Rankie only supports two frequencies, hourly and daily. Only text channels can be managed.\n\nUsage: {prefix}setManagedChannel <channel_name> <frequency>\n\nAliases: {prefix}smc\n\nExample: {prefix}setManagedChannel general daily```'
        await ctx.message.reply(msg)
    elif ('DELETEMANAGEDCHANNEL' == cmd or 'DMC' == cmd) and ctx.message.author.guild_permissions.manage_guild:
        msg = f'```Removes a managed channel from being managed. This channel will no longer have its messages periodically deleted at the requested frequency.\n\nUsage: {prefix}deleteManagedChannel <channel_name>\n\nAliases: {prefix}dmc\n\nExample: {prefix}deleteManagedChannel general```'
        await ctx.message.reply(msg)
    elif ('SETSAVEDMESSAGE' == cmd or 'SSM' == cmd) and ctx.message.author.guild_permissions.manage_guild:
        msg = f'```Sets a saved message in a managed channel. A saved message will not be deleted when performing channel management.\n\nUsage: {prefix}setSavedMessage <channel_name> <message_id>\n\nAliases: {prefix}ssm\n\nExample: {prefix}setSavedMessage general 862459611819016212```'
        await ctx.message.reply(msg)
    elif ('DELETESAVEDMESSAGE' == cmd or 'DSM' == cmd) and ctx.message.author.guild_permissions.manage_guild:
        msg = f'```Removes a saved message from a managed channel. This message will no longer be saved when performing channel management.\n\nUsage: {prefix}deleteSavedMessage <channel_name> <message_id>\n\nAliases: {prefix}dsm\n\nExample: {prefix}deleteSavedMessage general 862459611819016212```'
        await ctx.message.reply(msg)
    elif ('LISTMANAGEDCHANNELS' == cmd or 'LMC' == cmd) and ctx.message.author.guild_permissions.manage_guild:
        msg = f'```Lists all the current channels being managed by Rankie in this server.\n\nUsage: {prefix}listManagedChannels\n\nAliases: {prefix}lmc```'
        await ctx.message.reply(msg)
    elif ('LISTSAVEDMESSAGES' == cmd or 'LSM' == cmd) and ctx.message.author.guild_permissions.manage_guild:
        msg = f'```Lists all the saved messages for a managed channel in this server.\n\nUsage: {prefix}listSavedMessages <channel_name>\n\nAliases: {prefix}lsm\n\nExample: {prefix}listSavedMessages general```'
        await ctx.message.reply(msg)
    else:
        msg = 'Available Commands:\n```'
        msg += f'{prefix}assignRank <region>/<realm>/<name>\n\n'
        msg += f'{prefix}profile <region>/<realm>/<name>\n\n'
        msg += f'{prefix}listRanks\n\n'

        # If the user has manage_guild permissions, give them info on these commands
        if ctx.message.author.guild_permissions.manage_guild:
            msg += f'{prefix}setRank <IO_Range> [Rank Name]\n\n'
            msg += f'{prefix}deleteRank [Rank Name]\n\n'
            msg += f'{prefix}setPrefix <desired_prefix>\n\n'
            msg += f'{prefix}setSeason <desired_season>\n\n'
            msg += f'{prefix}setManagedChannel <channel_name> <frequency>\n\n'
            msg += f'{prefix}deleteManagedChannel <channel_name>\n\n'
            msg += f'{prefix}setSavedMessage <channel_name> <message_id>\n\n'
            msg += f'{prefix}deleteSavedMessage <channel_name> <message_id>\n\n'
            msg += f'{prefix}listManagedChannels\n\n'
            msg += f'{prefix}listSavedMessages <channel_name>\n\n'
            msg += '```'
        else:
            msg += '```'

        msg += f'\nRankie is currently using the __{get_season(ctx.guild.id)}__ season to calculate its scores for ranks.\n'
        msg += f'\nFor more information on a command, type ``{prefix}help <command_name>``'
        await ctx.message.reply(msg)

# Setup repeated tasks
rankie.loop.create_task(hourly_management())
rankie.loop.create_task(daily_management())

# Run the bot!
rankie.run(config['discordToken'])
