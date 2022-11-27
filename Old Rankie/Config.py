import json
import os

# This class holds all the json files and a few utility functions
class config:
    def __init__(self, logging, db):
        self.__logging = logging
        self.__db = db
        self.DEFAULT_PREFIX = '?'

        # Load the discord token
        self.__discord_token = os.environ.get('DISCORD_TOKEN')

    # Returns the discord token read from the environment
    def get_token(self):
        return self.__discord_token

    # Given a guild id, return its season setting (previous or current)
    def get_season(self, guild_id):
        try:
            season = self.__db.get_season(str(guild_id))

            # If the server has no existing season, set and return default
            if season == None:
                self.__db.set_season(str(guild_id), 'current')
                return 'current'
            # Else, return the set season
            else:
                return season[0]
        except Exception as e:
            self.__logging.error(f'Failed to get season: {e}')

    # Get the server prefix
    def get_prefix(self, client, message):
        try:
            prefix = self.__db.get_prefix(str(message.guild.id))

            # If the server has no existing prefix, set and return default
            if prefix == None:
                self.__db.set_prefix(str(message.guild.id), self.DEFAULT_PREFIX)
                return self.DEFAULT_PREFIX
            # Else, return the set prefix
            else:
                return prefix[0]
        except Exception as e:
            self.__logging.error(f'Failed to get prefix: {e}')

            #? BUGFIX: If we fail to get a prefix don't return none as this crashes the bot
            return self.DEFAULT_PREFIX

    # Sets the prefix for a guild
    async def set_prefix(self, ctx, desired_prefix):
        # Accept only prefixes of a single char
        if len(desired_prefix) == 1:
            try:
                self.__db.set_prefix(str(ctx.guild.id), str(desired_prefix))
            
                # Inform the user of the change
                await ctx.message.reply(f'Prefix successfully changed to: **{desired_prefix}**')
            except Exception as e:
                self.__logging.error(f'Failed to set prefix: {e}')
                await ctx.message.reply('Failed to set prefix due to a database error. Please try again later.')

        # An invalid prefix was sent
        else:
            await ctx.message.reply(f'Desired prefix {desired_prefix} is invalid. Prefix must be a single character.')
