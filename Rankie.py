import json
import discord
import aiohttp

from discord.ext import commands

#TODO: Add a logger
#TODO: Change bot status once every 24 hrs to something funny
#TODO: Create custom help with permission intelligence (still lacking permission intelligence)

#? Permissions required: manage_roles, 

#? Default prefix for Rankie
DEFAULT_PREFIX = '?'

#? The top cap for scores. Lets hope an IO score can never be greater than 99999
INFINITY = 99999

# Load config
with open('./config/config.json', 'r') as config:
    config = json.loads(config.read())

# Load prefixes
with open('./config/prefixes.json', 'r') as prefixes:
    prefixes = json.loads(prefixes.read())

# Load roles
with open('./config/roles.json', 'r') as roles:
    roles = json.loads(roles.read())

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
def detect_overlap(guild_id, IO_range, role_id):
    # If roles exist for this guild
    if str(guild_id) in roles:
        existing_roles = roles[str(guild_id)]
        IO_range = parse_IO_range(IO_range)

        for role in existing_roles:
            # If the role id matches, a role of that name already exists
            if role[0] == role_id:
                return False

            # If the IO range overlaps, it is invalid
            saved_range = parse_IO_range(role[1])
            if max(IO_range) >= min(saved_range) and min(saved_range) >= max(IO_range):
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

async def add_role(ctx, role, IO_range):
    # Verify the passed IO range is valid
    try:
        # Verify the passed IO range does not overlap with an existing saved range
        if not detect_overlap(ctx.guild.id, IO_range, role.id):
            await ctx.message.reply(f'The rank or IO range passed already exists.')
            return
    except Exception as e:
        print(e)
        await ctx.message.reply(f'I didn\'t recognize that command. Try asking me: **{prefixes[str(ctx.guild.id)]}help setRank**')
        return

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
        async with session.get(f'https://raider.io/api/v1/characters/profile?region={region}&realm={realm}&name={name}&fields=mythic_plus_scores_by_season%3Acurrent') as response:
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
rankie = commands.Bot(command_prefix=get_prefix, help_command=None)

#? BOT EVENTS

@rankie.event
async def on_ready():
    print('Rankie Successfully Started!')

@rankie.event
async def on_command_error(ctx, error):
    print(error)
    await ctx.message.reply(f'I didn\'t recognize that command. Try asking me **{prefixes[str(ctx.guild.id)]}help**')

@rankie.event
async def on_guild_join(guild):
    prefixes[str(guild.id)] = DEFAULT_PREFIX

    # Dump the new prefix into the JSON
    with open('./config/prefixes.json', 'w') as temp:
        json.dump(prefixes, temp, indent=4)

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
        print(e)
        await ctx.message.reply(f'I didn\'t recognize that command. Try asking me: **{prefixes[str(ctx.guild.id)]}help assignRank**')
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
        print(e)
        return    

    await ctx.message.reply(f'You have been assigned {discord.utils.get(ctx.message.guild.roles, id=rank_id)}. This rank is for players with an IO score of {dict(sorted_ranks)[rank_id]}.')     

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
        print(e)
        await ctx.message.reply(f'I didn\'t recognize that command. Try asking me: **{prefixes[str(ctx.guild.id)]}help profile**')
        return

    await ctx.message.reply(profile_url)

@rankie.command(name='setRank', aliases=['sr'])
@commands.has_permissions(manage_guild=True)
async def set_rank(ctx, IO_range, *rank_name):

    # Capitalize all items
    rank_name = ' '.join(rank_name).title()

    # Determine if IO range is valid
    if not check_IO_range(IO_range):
        await ctx.message.reply(f'The IO range {IO_range} is invalid.')
        return

    # Look at existing roles in the guild
    check_for_dupe = discord.utils.get(ctx.message.guild.roles, name=rank_name)

    # If check for dupe is false, the role does not exist
    if check_for_dupe == None:
        # Attemp to create the role
        try:
            role = await ctx.guild.create_role(name=rank_name)
        except Exception as e:
            print(e)
            await ctx.message.reply('Failed to create the requested rank. This is likely due to a permissions issue. Please make sure Rankie has the ability to create roles or manually create the role before setting the rank.')
            return

    # Else the role already exists
    else:
        role = check_for_dupe

    # Add the role
    await add_role(ctx, role, IO_range)

@rankie.command(name='deleteRank', aliases=['dr'])
@commands.has_permissions(manage_guild=True)
async def delete_rank(ctx, *rank_name):
    rank_name = ' '.join(rank_name).title()

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
        print(e)
        await ctx.message.reply(f'Successfully deleted the rank {rank_name} internally. However, failed to delete the role on the server. This is likely a permissions issue. Please make sure Rankie has the ability to delete roles or manually delete the role.')
        return

    await ctx.message.reply(f'Successfully deleted the rank {rank_name}.')

@rankie.command(name='listRanks', aliases=['lr'])
async def list_ranks(ctx):
    sorted_ranks = get_sorted_ranks(ctx.guild.id)
    msg = f'Currently set ranks:\n```{"Rank Name":<20}\t{"IO Range":<20}\n'
    msg += f'{"---------":<20}\t{"--------":<20}\n'

    for item in sorted_ranks:
        rank_name = str(discord.utils.get(ctx.message.guild.roles, id=item[0]))
        msg += f'{rank_name:<20}\t{item[1]:<20}\n'

    msg += '```'
    await ctx.message.reply(msg)

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

@rankie.command(name='help', aliases=['h'])
async def help(ctx, *cmd):
    prefix = prefixes[str(ctx.guild.id)]
    cmd = ' '.join(cmd)
    cmd = cmd.upper()

    if 'ASSIGNRANK' == cmd or 'AR' == cmd:
        msg = f'```Assigns a rank based on your current Raider.io score.\n\nUsage: {prefix}assignRank <region>/<realm>/<name>\n\nAliases: {prefix}ar\n\nExample: {prefix}assignRank us/aggramar/sapphirre```'
        await ctx.message.reply(msg)
    elif 'PROFILE' == cmd or 'P' == cmd:
        msg = f'```Return the URL for a characters Raider.io profile.\n\nUsage: {prefix}profile <region>/<realm>/<name>\n\nAliases: {prefix}p\n\nExample: {prefix}profile us/aggramar/sapphirre```'
        await ctx.message.reply(msg)
    elif 'LISTRANKS' == cmd or 'LR' == cmd:
        msg = f'```Lists all the currently set ranks for this server.\n\nUsage: {prefix}listRanks\n\nAliases: {prefix}lr```'
        await ctx.message.reply(msg)
    elif 'SETRANK' == cmd or 'SR' == cmd:
        msg = f'```Adds a rank attached to a specified IO range. When a member asks to be assigned a rank and their IO score is within this range, the associated rank will be assigned.\n\nUsage: {prefix}setRank <IO_Range> [Rank Name]\n\nAliases: {prefix}sr\n\nExample: {prefix}setRank 0-1000 Baby\nExample: {prefix}setRank 1000+ Bigger Baby\n\nNote, the IO range passed or the rank name cannot overlap with existing managed ranks. In addition, the end value of a range is exclusive. This means that the range 0-1000 maxes out at 999.```'
        await ctx.message.reply(msg)
    elif 'DELETERANK' == cmd or 'DR' == cmd:
        msg = f'```Deletes a rank that already exists.\n\nUsage: {prefix}deleteRank [Rank Name]\n\nAliases: {prefix}dr\n\nExample: {prefix}deleteRank Bigger Baby```'
        await ctx.message.reply(msg)
    elif 'SETPREFIX' == cmd or 'SP' == cmd:
        msg = f'```Sets the prefix that Rankie uses for this server.\n\nUsage: {prefix}setPrefix <desired_prefix>\n\nAliases: {prefix}sp\n\nExample: {prefix}setPrefix !```'
        await ctx.message.reply(msg)
    else:
        msg = 'Available Commands:```'
        msg += f'{prefix}assignRole <region>/<realm>/<name>\n\n'
        msg += f'{prefix}profile <region/<realm/<name>\n\n'
        msg += f'{prefix}listRanks\n\n'
        msg += f'{prefix}setRank <IO_Range> [Rank Name] - (Requires Management Role)\n\n'
        msg += f'{prefix}deleteRank [Rank Name] - (Requires Management Role)\n\n'
        msg += f'{prefix}setPrefix <desired_prefix> - (Requires Management Role)\n\n```'
        msg += f'\nFor more information on a command, type ``{prefix}help <command_name>``'
        await ctx.message.reply(msg)

# Run the bot!
rankie.run(config['discordToken'])