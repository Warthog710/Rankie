import discord
class channel_management:
    def __init__(self, logging, cfg, db):
        self.__logging = logging
        self.__cfg = cfg
        self.__db = db

    # Sets an existing channel to be managed by Rankie (a managed channel has its messages deleted periodically)
    async def set_managed_channel(self, ctx, channel_name, frequency):
        channel = discord.utils.get(ctx.message.guild.channels, name=channel_name)

        # If channel_name is none it does not exist
        if channel == None:
            await ctx.message.reply(f'I couldn\'t find a channel with the name __{channel_name}__.')
            return

        # Only allow text channels
        if str(channel.type) == 'voice' or str(channel.type) == 'store' or str(channel.type) == 'stage_voice':
            await ctx.message.reply(f'Only text channels can be managed.')
            return

        # If frequency is not hourly or daily throw an error
        frequency = frequency.lower()
        if frequency != 'hourly' and frequency != 'daily':
            await ctx.message.reply('Received an invalid frequency. Only __daily__ and __hourly__ are accepted.')
            return

        # Set the managed channel if it does not exist
        try:
            managed_channels = self.__db.get_managed_channels_for_guild(str(ctx.guild.id))
        except Exception as e:
            self.__logging.error(f'Failed to set a managed channel: {e}')
            await ctx.message.reply('Failed to set managed channel due to a database error. Please try again later.')
        else:
            # Check if the channel is already being managed
            for item in managed_channels:
                if item[0] == str(channel.id):
                    await ctx.message.reply(f'The channel __{channel_name}__ is already managed.')
                    return

            # The channel does not exist, set it
            try:
                self.__db.set_managed_channel_for_guild(str(ctx.guild.id), str(channel.id), frequency)
            except Exception as e:
                self.__logging.error(f'Failed to set managed channel: {e}')
                await ctx.message.reply('Failed to set managed channel due to a database error. Please try again later.')
            else:
                await ctx.message.reply(f'The channel __{channel_name}__ is now being managed by Rankie on a __{frequency}__ basis.')

    # Removes an existing channel from management, the channel itself is not affected.
    async def delete_managed_channel(self, ctx, channel_name):
        channel = discord.utils.get(ctx.message.guild.channels, name=channel_name)

        # If channel is none it does not exist
        if channel == None:
            await ctx.message.reply(f'I couldn\'t find a channel with the name __{channel_name}__.')
            return

        try:
            managed_channels = self.__db.get_managed_channels_for_guild(str(ctx.guild.id))
        except Exception as e:
            self.__logging.error(f'Failed to delete managed channels: {e}')
            await ctx.message.reply('Failed to delete a managed channel due to a database error. Please try again later.')
        # Delete the managed channel from managed channels if it is being managed
        else:
            for item in managed_channels:
                if str(channel.id) in item[0]:
                    try:
                        self.__db.del_managed_channel_from_guild(str(ctx.guild.id), str(channel.id))

                        # Also delete all saved message related to that channel
                        self.__db.del_all_saved_messages_from_channel(str(channel.id))
                    except Exception as e:
                        self.__logging.error(f'Failed to delete managed channels: {e}')
                        await ctx.message.reply('Failed to delete a managed channel due to a database error. Please try again later.')
                    else:
                        await ctx.message.reply(f'The channel __{channel_name}__ will no longer be managed by Rankie.')
                        return

            # Channel is not already managed
            await ctx.message.reply(f'The channel __{channel_name}__ is not managed by Rankie.')

    # Sets a saved message in a managed channel, this message will not be deleted
    async def set_saved_message(self, ctx, channel_name, message_id):
        channel = discord.utils.get(ctx.message.guild.channels, name=channel_name)

        # If channel is none it does not exist
        if channel == None:
            await ctx.message.reply(f'I couldn\'t find a channel with the name __{channel_name}__.')
            return

        # If the passed id is not numeric, then its not a valid id
        if not message_id.isnumeric():
            await ctx.message.reply(f'The ID {message_id} is not valid.')
            return

        try:
            msg = await channel.fetch_message(int(message_id))
        except Exception as e:
            self.__logging.info(f'Failed to find a message in {channel_name}. message_id={message_id}: {e}')
            await ctx.message.reply(f'Failed to find a message in __{channel_name}__ associated with the passed ID __{message_id}__')
            return

        # Verify that Rankie is currently managing that channel
        try:
            managed_channels = self.__db.get_managed_channels_for_guild(str(ctx.guild.id))
        except Exception as e:
            self.__logging.error(f'Failed to set a saved message: {e}')
            await ctx.message.reply('Failed to set a saved message due to a database error. Please try again later.')
        else:
            for item in managed_channels:
                if str(channel.id) == item[0]:
                    # If the channel exists, set the saved message if it does not already exist
                    try:
                        saved_messages = self.__db.get_saved_messages_for_channel(str(item[0]))
                    except Exception as e:
                        self.__logging.error(f'Failed to set a saved message: {e}')
                        await ctx.message.reply('Failed to set a saved message due to a database error. Please try again later.')
                        return
                    else:
                        # Verify the saved message does not already exist
                        for item in saved_messages:
                            if str(message_id) in item[0]:
                                await ctx.message.reply(f'The message __{msg.id}__ is already being saved by Rankie.')
                                return

                        # Set the saved message
                        try:
                            self.__db.set_saved_message_for_guild(str(channel.id), str(message_id))
                        except Exception as e:
                            self.__logging.error(f'Failed to set a saved message: {e}')
                            await ctx.message.reply('Failed to set a saved message due to a database error. Please try again later.')
                            return
                        else:
                            await ctx.message.reply(f'The message __{msg.id}__ in __{channel_name}__ will now be saved by Rankie.')
                            return

            # If the channel is not present, it is not currently being managed
            await ctx.message.reply(f'The channel {channel_name} is not currently managed by Rankie, please ask Rankie to manage this channel before setting any saved message(s).')

    # Removes a saved message from a managed channel, this message will no longer be saved when performing periodic deletion
    async def delete_saved_message(self, ctx, channel_name, message_id):
        channel = discord.utils.get(ctx.message.guild.channels, name=channel_name)

        # If channel is none it does not exist
        if channel == None:
            await ctx.message.reply(f'I couldn\'t find a channel with the name __{channel_name}__.')
            return

        # If the passed id is not numeric, then its not a valid id
        if not message_id.isnumeric():
            await ctx.message.reply(f'The ID {message_id} is not valid.')
            return

        try:
            managed_channels = self.__db.get_managed_channels_for_guild(str(ctx.guild.id))
        except Exception as e:
            self.__logging.error(f'Failed to delete saved messages: {e}')
            await ctx.message.reply('Failed to delete saved messages due to a database error. Please try again later.')
        else:
            for item in managed_channels:
                # The channel is being managed
                if str(channel.id) == item[0]:
                    try:
                        saved_messages = self.__db.get_saved_messages_for_channel(str(channel.id))
                    except Exception as e:
                        self.__logging.error(f'Failed to delete saved messages: {e}')
                        await ctx.message.reply('Failed to delete saved messages due to a database error. Please try again later.')
                    else:
                        for msg in saved_messages:
                            # The message exists delete it
                            if str(message_id) == msg[0]:
                                try:
                                    self.__db.del_saved_message_from_channel(str(channel.id), str(message_id))
                                except Exception as e:
                                    self.__logging.error(f'Failed to delete saved messages: {e}')
                                    await ctx.message.reply('Failed to delete saved messages due to a database error. Please try again later.')
                                    return
                                else:
                                    await ctx.message.reply(f'The message __{message_id}__ will NO longer be saved by Rankie.')
                                    return

                        # The message ID is not saved or does not exist
                        await ctx.message.reply(f'The message __{message_id}__ is not being saved or the passed message ID is invalid.')
                        return

            # The channel is not currently being managed
            await ctx.message.reply(f'The channel __{channel_name}__ is not currently managed by Rankie, please ask Rankie to manage this channel before deleting any saved message(s).')

    # Prints a list of all of the currently managed channels to the requested channel
    async def list_managed_channels(self, ctx):
        try:
            managed_channels = self.__db.get_managed_channels_for_guild(str(ctx.guild.id))
        except Exception as e:
            self.__logging.error(f'Failed to list managed channels: {e}')
            await ctx.message.reply('Failed to list managed channels due to a database error. Please try again later.')
        else:
            # Check if the guild has managed channels
            if len(managed_channels) > 0:
                msg = f'Managed channels:\n```{"Channel":<20}\t{"Frequency":<20}\n{"-------":<20}\t{"---------":<20}\n'

                for channel_id in managed_channels:
                    channel_name = str(discord.utils.get(ctx.message.guild.channels, id=int(channel_id[0])))
                    msg += f'{channel_name:<20}\t{channel_id[1]:<10}\n'

                msg += '```'
                await ctx.message.reply(msg)
            else:
                await ctx.message.reply(f'This server has no currently managed channels. Please ask **{self.__cfg.get_prefix(None, ctx.message)}help setManagedChannel** to learn how to set managed channels.')

    # Prints a list of all the currently saved messages in a managed channel to the requested channel
    async def list_managed_messages(self, ctx, channel_name):
        channel = discord.utils.get(ctx.message.guild.channels, name=channel_name)

        # If channel is none it does not exist
        if channel == None:
            await ctx.message.reply(f'I couldn\'t find a channel with the name __{channel_name}__.')
            return

        try:
            managed_channels = self.__db.get_managed_channels_for_guild(str(ctx.guild.id))
        except Exception as e:
            self.__logging.error(f'Failed to list saved messages: {e}')
            await ctx.message.reply('Failed to list saved messages due to a database error. Please try again later.')
        else:
            for item in managed_channels:
                # The channel is being managed
                if str(channel.id) == item[0]:
                    try:
                        saved_messages = self.__db.get_saved_messages_for_channel(str(channel.id))
                    except Exception as e:
                        self.__logging.error(f'Failed to list saved messages: {e}')
                        await ctx.message.reply('Failed to list saved messages due to a database error. Please try again later.')
                    else:
                        # If the length of saved message is > 0
                        if len(saved_messages) > 0:
                            msg = f'Saved message(s) in __{channel_name}__:\n'
                            for msg_id in saved_messages:
                                msg += f'``{msg_id[0]}``\n'
                            await ctx.message.reply(msg)
                            return
                        else:
                            await ctx.message.reply(f'The channel __{channel_name}__ has no saved messages.')
                            return
            
            # The channel must not be managed by Rankie
            await ctx.message.reply(f'The channel __{channel_name}__ is not currently being managed by Rankie.')