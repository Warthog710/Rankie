import asyncio

from datetime import datetime, timedelta
from discord import Activity, ActivityType, Status
class tasks:
    def __init__(self, rankie, logging, db):
        self.__rankie = rankie
        self.__logging = logging
        self.__db = db

    # Triggers hourly
    async def channel_management(self):
        await self.__rankie.wait_until_ready()
        daily_management = False

        # Sleep until the next hour
        next_hour = (datetime.now() + timedelta(hours=1)).replace(microsecond=0, second=0, minute=0)
        wait_seconds = (next_hour - datetime.now()).seconds
        await asyncio.sleep(wait_seconds + 1)

        while not self.__rankie.is_closed():
            if datetime.now().hour == 0:
                self.__logging.info('Starting hourly management')
                daily_management = True
            else:
                self.__logging.info('Starting hourly & daily management')

            # Get managed channels
            try:
                managed_channels = self.__db.get_all_managed_channels()

                # For all managed channels
                for channel in managed_channels:
                    # Perform hourly management
                    if not daily_management:
                        if 'hourly' in channel[1]:
                            # Get all saved messages for that channel
                            saved_messages = self.__db.get_saved_messages_for_channel(str(channel[0]))
                            await self.__purge_channel(int(channel[0]), self.__convert_to_list(saved_messages))
                    else:
                        # Get all saved messages for that channel
                        saved_messages = self.__db.get_saved_messages_for_channel(str(channel[0]))
                        await self.__purge_channel(int(channel[0]), self.__convert_to_list(saved_messages))

            except Exception as e:
                self.__logging.error(f'Failed to fetch all managed channels or messages: {e}')

            # Reset daily management
            daily_management = False

            # Log completion
            self.__logging.info('Finished channel management.')

            # Sleep until the next hour
            next_hour = (datetime.now() + timedelta(hours=1)).replace(microsecond=0, second=0, minute=0)
            wait_seconds = (next_hour - datetime.now()).seconds
            await asyncio.sleep(wait_seconds + 1)

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

    # Converst a list of tuples to a list only containing the first item
    def __convert_to_list(self, my_list):
        temp = []
        for item in my_list:
            temp.append(item[0])
        return temp
            
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
                if str(message.id) in reserved_messages:
                    continue
                else:
                    await message.delete()

                    # Discord rate limits you while deleting messages in this fashion. Sleeping for 1 second between deletions seems to resolve this
                    await asyncio.sleep(1)
        except Exception as e:
            self.__logging.info(f'Failed to delete messages in managed channel {channel_id}: {e}')
            await channel.send('Rankie attempted to manage this channel but failed. This is likely due to missing permissions. Please make sure Rankie has permission to __manage messages__ and __read message history__.')
