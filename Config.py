import json
import os

# This class holds all the json files and a few utility functions
class config:
    def __init__(self, logging):
        self.__logging = logging
        self.__DEFAULT_PREFIX = '?'

        # Make sure the folder exists
        if not os.path.exists('./config'):
            os.mkdir('./config')

        # Load config
        try:
            with open('./config/config.json', 'r') as config:
                self.config = json.loads(config.read())
        except Exception as e:
            self.__logging.error(f'./config/config.json was not found: {e}')
            self.config = {}

        # Load prefixes
        try:
            with open('./config/prefixes.json', 'r') as prefixes:
                self.prefixes = json.loads(prefixes.read())
        except Exception as e:
            self.__logging.warning(f'./config/prefixes.json was not found! prefixes will be set to an empty dictionary: {e}')
            self.prefixes = {}

        # Load roles
        try:
            with open('./config/roles.json', 'r') as roles:
                self.roles = json.loads(roles.read())
        except Exception as e:
            self.__logging.warning(f'./config/roles.json was not found! roles will be set to an empty dictionary: {e}')
            self.roles = {}

        # Load season
        try:
            with open('./config/season.json', 'r') as season:
                self.season = json.loads(season.read())
        except Exception as e:
            self.__logging.warning(f'./config/season.json was not found! season will be set to an empty dictionary: {e}')
            self.season = {}

        # Load managed guilds
        try:
            with open('./config/managed_guilds.json', 'r') as managed_guilds:
                self.managed_guilds = json.loads(managed_guilds.read())
        except Exception as e:
            self.__logging.warning(f'./config/managed_guilds.json was not found! managed_guilds will be set to an empty dictionary: {e}')
            self.managed_guilds = {}

        # Load managed channels
        try:
            with open('./config/managed_channels.json', 'r') as managed_channels:
                self.managed_channels = json.loads(managed_channels.read())
        except Exception as e:
            self.__logging.warning(f'./config/managed_channels.json was not found! managed_channels will be set to an empty dictionary: {e}')
            self.managed_channels = {}

    # Take the name of a json file and dumps it to disk
    def dump_json(self, file, name):
        with open(f'./config/{name}.json', 'w') as dump:
            json.dump(file, dump, indent=4)

    # Given a guild id, return its season setting (previous or current)
    def get_season(self, guild_id):
        if str(guild_id) in self.season:
            return self.season[str(guild_id)]

        # Else, the server setting has not been set, set to default
        else:
            self.season[str(guild_id)] = 'current'

    # Get the server prefix
    def get_prefix(self, client, message):
        if str(message.guild.id) in self.prefixes:
            return self.prefixes[str(message.guild.id)]
        
        # Else, the server prefix has not been set, set to default
        else:
            self.prefixes[str(message.guild.id)] = self.__DEFAULT_PREFIX

            # Return default prefix
            return self.__DEFAULT_PREFIX

    # Sets the prefix for a guild
    async def set_prefix(self, ctx, desired_prefix):
        # Accept only prefixes of a single char
        if len(desired_prefix) == 1:
            self.prefixes[str(ctx.guild.id)] = desired_prefix
            
            # Inform the user of the change
            await ctx.message.reply(f'Prefix successfully changed to: **{desired_prefix}**')

        # An invalid prefix was sent
        else:
            await ctx.message.reply(f'Desired prefix {desired_prefix} is invalid. Prefix must be a single character.')
