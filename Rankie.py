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

DEFAULT_PREFIX = '?'

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

@rankie.command(name='setRank', aliases=['sr'], help='UPDATE ME!!!')
async def set_rank(ctx, *cmd):
    pass

@rankie.command(name='deleteRank', aliases=['dr'], help='UPDATE ME!!!')
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

    # An invalid prefix was sen
    else:
        await ctx.message.reply(f'Desired prefix was invalid. Prefix must be a single character.')

# Run the bot!
rankie.run(config['discordToken'])