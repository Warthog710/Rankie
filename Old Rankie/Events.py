class events:
    def __init__(self, logging, cfg, db):
        self.__logging = logging
        self.__cfg = cfg
        self.__db = db

    async def on_ready(self):
        self.__logging.info('Rankie successfully started!')
        print('Rankie Successfully Started!')

    async def on_command_error(self, ctx, error):
        self.__logging.info(f'Unspecified command error occurred: {error}')
        await ctx.message.reply(f'I didn\'t recognize that command. Try asking me **{self.__cfg.get_prefix(None, ctx.message)}help**')

    async def on_guild_join(self, guild):
        self.__logging.info(f'Rankie joined {guild.id}')
        
        try:
            self.__db.set_prefix(str(guild.id), self.__cfg.DEFAULT_PREFIX)
        except Exception as e:
            self.__logging.error(f'Failed to set prefix on joining guild {guild.id}: {e}')

    async def on_guild_remove(self, guild):
        self.__logging.info(f'Rankie left {guild.id}')

        # Clean up prefixes
        try:
            self.__db.del_prefix(str(guild.id))
        except Exception as e:
            self.__logging.error(f'Failed to delete prefix on leaving guild {guild.id}: {e}')   

        # Clean up roles
        try:
            self.__db.del_all_roles_for_guild(str(guild.id))
        except Exception as e:
            self.__logging.error(f'Failed to delete roles on leaving guild {guild.id}: {e}')  

        # Clean up season
        try:
            self.__db.del_season(str(guild.id))
        except Exception as e:
            self.__logging.error(f'Failed to delete season on leaving guild {guild.id}: {e}')  

        try:
            managed_channels = self.__db.get_managed_channels_for_guild(str(guild.id))

            for channel in managed_channels:
                # Del all saved messages for that channel
                self.__db.del_all_saved_messages_from_channel(str(channel[0]))

            # Delete all managed channels for guild
            self.__db.del_all_managed_channels_from_guild(str(guild.id))
        except Exception as e:
            self.__logging.error(f'Failed to delete managed channels and saved messages on leaving guild {guild.id}: {e}') 