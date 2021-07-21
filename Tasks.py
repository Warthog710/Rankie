import asyncio

from datetime import datetime, timedelta
from discord import Activity, ActivityType, Status
class tasks:
    def __init__(self, rankie, logging, cfg):
        self.__rankie = rankie
        self.__logging = logging
        self.__cfg = cfg

    # Triggers hourly
    async def channel_management(self):
        await self.__rankie.wait_until_ready()
        daily_management = False

        # Sleep until the next hour
        next_hour = (datetime.now() + timedelta(hours=1)).replace(microsecond=0, second=0, minute=0)
        wait_seconds = (next_hour - datetime.now()).seconds
        await asyncio.sleep(wait_seconds)

        while not self.__rankie.is_closed():
            if datetime.now().hour == 0:
                self.__logging.info('Performing daily and hourly channel management.')
                daily_management = True
            else:
                self.__logging.info('Performing hourly channel management.')

            for guild_id in self.__cfg.managed_guilds:
                for channel_id in self.__cfg.managed_guilds[str(guild_id)]:

                    # Perform hourly management
                    if not daily_management:
                        if self.__cfg.managed_channels[str(channel_id)][0] == 'hourly':
                            await self.__purge_channel(channel_id, self.__cfg.managed_channels[str(channel_id)][1])
                    # Perform daily and hourly management
                    else:
                            await self.__purge_channel(channel_id, self.__cfg.managed_channels[str(channel_id)][1])

            # Reset daily management
            daily_management = False

            # Log completion
            self.__logging.info('Channel management complete.')

            # Sleep until the next hour
            next_hour = (datetime.now() + timedelta(hours=1)).replace(microsecond=0, second=0, minute=0)
            wait_seconds = (next_hour - datetime.now()).seconds
            await asyncio.sleep(wait_seconds)

    # Triggers daily to change bot status
    async def change_status(self):
        await self.__rankie.wait_until_ready()

        # Change the bot status while running every 24hrs and on start
        while not self.__rankie.is_closed():
            await self.__rankie.change_presence(activity=Activity(type=ActivityType.watching, name='for queries...'), status=Status.online)

            # Sleep until the next day
            next_day = (datetime.now() + timedelta(days=1)).replace(microsecond=0, second=0, minute=0, hour=0)
            wait_seconds = (next_day - datetime.now()).seconds
            await asyncio.sleep(wait_seconds)

    # Triggers daily to save all settings to disk
    async def save_json(self):
        await self.__rankie.wait_until.ready()

        # Sleep until the next day
        next_day = (datetime.now() + timedelta(days=1)).replace(microsecond=0, second=0, minute=0, hour=0)
        wait_seconds = (next_day - datetime.now()).seconds
        await asyncio.sleep(wait_seconds)

        while not self.__rankie.is_closed():
            self.__logging.info('Performing daily dictionary save.')

            # Dump config
            self.__cfg.dump_json(self.__cfg.config, 'config')

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

            self.__logging.info('Successfully saved dictionaries.')

            # Sleep until the next day
            next_day = (datetime.now() + timedelta(days=1)).replace(microsecond=0, second=0, minute=0, hour=0)
            wait_seconds = (next_day - datetime.now()).seconds
            await asyncio.sleep(wait_seconds)

    # Given a channel_id, delete all of its messaged except for those that have ID's in reserved messages
    async def __purge_channel(self, channel_id, reserved_messages):
        # Attempt to fetch channel
        try:
            channel = await self.__rankie.fetch_channel(channel_id)
        except Exception as e:
            self.__logging.info(f'Failed to fetch managed channel {channel_id}: {e}')
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
            self.__logging.info(f'Failed to delete messages in managed channel {channel_id}: {e}')
            await channel.send('Rankie attempted to manage this channel but failed. This is likely due to missing permissions. Please make sure Rankie has permission to __manage messages__ and __read message history__.')
