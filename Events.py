class events:
    def __init__(self, logging, cfg):
        self.__logging = logging
        self.__cfg = cfg

    async def on_ready(self):
        self.__logging.info('Rankie successfully started!')
        print('Rankie Successfully Started!')

    async def on_command_error(self, ctx, error):
        self.__logging.info(f'Unspecified command error occurred: {error}')
        await ctx.message.reply(f'I didn\'t recognize that command. Try asking me **{self.__get_prefix(None, ctx.message)}help**')

    async def on_guild_join(self, guild):
        self.__logging.info(f'Rankie joined {guild.id}')
        self.__cfg.prefixes[str(guild.id)] = self.__cfg.DEFAULT_PREFIX

        # Dump the new prefix to disk
        self.__cfg.dump_json(self.__cfg.prefixes, 'prefixes')

    async def on_guild_remove(self, guild):
        self.__logging.info(f'Rankie left {guild.id}')

        # Clean up prefixes
        if str(guild.id) in self.__cfg.prefixes:
            del self.__cfg.prefixes[str(guild.id)]

            # Dump the prefixes to disk
            self.__cfg.dump_json(self.__cfg.prefixes, 'prefixes')            

        # Clean up roles
        if str(guild.id) in self.__cfg.roles:
            del self.__cfg.roles[str(guild.id)]

            # Dump the roles to disk
            self.__cfg.dump_json(self.__cfg.roles, 'roles')

        # Clean up season
        if str(guild.id) in self.__cfg.season:
            del self.__cfg.season[str(guild.id)]

            # Dump the seasons to disk
            self.__cfg.dump_json(self.__cfg.season, 'season')

        # Clean up managed_channels
        if str(guild.id) in self.__cfg.managed_guilds:
            temp = self.__cfg.managed_guilds[str(guild.id)]
            del self.__cfg.managed_guilds[str(guild.id)]

            for channel_id in temp:
                if str(channel_id) in self.__cfg.managed_channels:
                    del self.__cfg.managed_channels[str(channel_id)]

            # Dump managed_guilds and managed_channels to disk
            self.__cfg.dump_json(self.__cfg.managed_guilds, 'managed_guilds')
            self.__cfg.dump_json(self.__cfg.managed_channels, 'managed_channels')