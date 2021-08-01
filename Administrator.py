import discord

class administrator:
    def __init__(self, cfg, logging):
        self.__cfg = cfg
        self.__logging = logging

    # Attaches and sends managed_channels to a discord message
    async def get_config_file(self, ctx, name):

        # Dump files so that we have the latest version
        self.__dump_dictionaries()
        
        try:
            if 'log' in name:
                await ctx.message.reply(file=discord.File(f'logs/rankie.log'))
            else:
                await ctx.message.reply(file=discord.File(f'config/{name}.json'))
        except Exception as e:
            self.__logging.error(f'Failed to deliver {name}.json for download due to error: {e}')
            await ctx.message.reply(f'Error: {e}')

    def __dump_dictionaries(self):
        # Dump managed_channels
        self.__cfg.dump_json(self.__cfg.managed_channels, 'managed_channels')

        # Dump managed_guilds
        self.__cfg.dump_json(self.__cfg.managed_guilds, 'managed_guilds')

        # Dump prefixes
        self.__cfg.dump_json(self.__cfg.prefixes, 'prefixes')

        # Dump roles
        self.__cfg.dump_json(self.__cfg.roles, 'roles')

        # Dump season
        self.__cfg.dump_json(self.__cfg.season, 'season')


