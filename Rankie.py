import json
import discord
import aiohttp

from discord.ext import commands

#TODO: ?assignRole
    # Given a region, realm, and name. Assign a role based on their IO score. If no role exists, return an error
#TODO: ?profile
    # Given a region, realm, and name. Return a URL for that players Raider.io profile
#TODO: ?setRank
    # Only for admins or the bot creator, set roles used by the bot
#TODO: ?deleteRank
    # Only for admins or the bot creator, delete roles used by the bot
#TODO" ?listRanks
    # List all the currently set roles and their IO ranges

#TODO: Add a logger
#TODO: Change bot status once every 24 hrs to something funny
#TODO: Create custom help with permission intelligence

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
                return False

    # The string contains a -
    elif '-' in IO_range:
        temp_min, temp_max = IO_range.split('-')

        if temp_max.isnumeric() and temp_min.isnumeric():
            if int(temp_min) >= 0:
                if int(temp_min) < int(temp_max):
                    return False

    return True

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
                return True

            # If the IO range overlaps, it is invalid
            saved_range = parse_IO_range(role[1])
            if max(saved_range) >= min(IO_range) and min(saved_range) >= max(IO_range):
                return True

        # If no overlap was detected, the range is good.
        return False

    # Else, no roles exist for this guild, no overlap can occur
    else:
        return False

async def add_role(ctx, role, IO_range):
    # Verify the passed IO range is valid
    try:
        if check_IO_range(IO_range):
            await ctx.message.reply(f'The IO range passed is invalid.')
            return

        # Verify the passed IO range does not overlap with an existing saved range
        if detect_overlap(ctx.guild.id, IO_range, role.id):
            await ctx.message.reply(f'The role or IO range passed already exists.')
            return
    except Exception as e:
        print(e)
        await ctx.message.reply('I didn\'t recognize that command. Try asking me: **!help setRank**')
        return

    # Add the role
    if str(ctx.guild.id) in roles:
        roles[str(ctx.guild.id)].append((role.id, IO_range))
    else:
        roles[str(ctx.guild.id)] = [(role.id, IO_range)]

    # Dump roles to disk
    with open('./config/roles.json', 'w') as temp:
        json.dump(roles, temp, indent=4)

    await ctx.message.reply(f'Successfully created the role {role} with an assigned IO range of {IO_range}.')

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
rankie = commands.Bot(command_prefix=get_prefix)

#? BOT EVENTS

@rankie.event
async def on_ready():
    print('Rankie Successfully Started!')

#? BOT COMMANDS

@rankie.command(name='assignRole', aliases=['ar'], help='Assigns a rank based on your current Raider.io score.\n\nUsage: ?assignRole <region>/<realm>/<name>\n\nExample: ?assignRole us/aggramar/sapphirre')
async def assign_role(ctx, *cmd):
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
        await ctx.message.reply('I didn\'t recognize that command. Try asking me: **!help assignRole**')
        return

    print(f'{region} & {realm} & {name}')
    print(mythic_score)

@rankie.command(name='profile', aliases=['p'], help='Return the URL for a characters Raider.io profile.\n\nUsage: ?profile <region>/<realm>/<name>\n\nExample: ?profile us/aggramar/sapphirre')
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
        await ctx.message.reply('I didn\'t recognize that command. Try asking me: **!help profile**')
        return

    await ctx.message.reply(profile_url)

@rankie.command(name='setRank', aliases=['sr'], help='Adds a role attached to a specified IO range. When a member asks to be assigned an IO score and they are within this range, this role will be assigned.\n\nUsage: ?setRank <IO_Range> <Role Name>\n\nExample: ?setRank 0-1000 Baby\nExample: ?setRank 1000+ Bigger Baby\n\nNote, the IO range passed or the role name cannot overlap with existing roles. In addition, the end value of a range is exclusive. This means that the range 0-1000 maxes out at 999.')
@commands.has_permissions(manage_guild=True)
async def set_rank(ctx, IO_range, *rank_name):

    # Capitalize all items
    rank_name = ' '.join(rank_name).title()

    # Look at existing roles in the guild
    check_for_dupe = discord.utils.get(ctx.message.guild.roles, name=rank_name)

    # If check for dupe is false, the role does not exist
    if check_for_dupe == None:
        # Attemp to create the role
        try:
            role = await ctx.guild.create_role(name=rank_name)
        except Exception as e:
            print(e)
            await ctx.message.reply('Failed to create the requested role. This is likely due to a permissions issue. Please make sure Rankie has the ability to create roles or manually create the role before setting the rank.')
            return

    # Else the role already exists
    else:
        role = check_for_dupe

    # Add the role
    await add_role(ctx, role, IO_range)

@rankie.command(name='deleteRank', aliases=['dr'], help='UPDATE ME!!!')
@commands.has_permissions(manage_guild=True)
async def delete_rank(ctx, *cmd):
    pass

@rankie.command(name='listRanks', aliases=['lr'], help='Lists all the currently set ranks for this server.\n\nUsage: ?listRanks')
async def list_ranks(ctx):
    pass

@rankie.command(name='setPrefix', aliases=['sp'], help='Sets the prefix that Rankie uses for this server.\n\nUsage: ?setPrefix <desired_prefix>')
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

# Run the bot!
rankie.run(config['discordToken'])