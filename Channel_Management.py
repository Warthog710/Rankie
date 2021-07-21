import discord

class channel_management:
    def __init__(self, logging, cfg):
        self.__logging = logging
        self.__cfg = cfg

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
        if str(channel.id) in self.__cfg.managed_channels:
            await ctx.message.reply(f'The channel __{channel_name}__ is already managed.')
        else:
            self.__cfg.managed_channels[str(channel.id)] = [frequency, []]

            if str(ctx.guild.id) in self.__cfg.managed_guilds:
                self.__cfg.managed_guilds[str(ctx.guild.id)].append(channel.id)
            else:
                self.__cfg.managed_guilds[str(ctx.guild.id)] = [channel.id]

            await ctx.message.reply(f'The channel __{channel_name}__ is now being managed by Rankie on a __{frequency}__ basis.')

    # Removes an existing channel from management, the channel itself is not affected.
    async def delete_managed_channel(self, ctx, channel_name):
        channel = discord.utils.get(ctx.message.guild.channels, name=channel_name)

        # If channel is none it does not exist
        if channel == None:
            await ctx.message.reply(f'I couldn\'t find a channel with the name __{channel_name}__.')
            return

        # Delete the managed channel from managed channels
        if str(channel.id) in self.__cfg.managed_channels:
            del self.__cfg.managed_channels[str(channel.id)]
        else:
            await ctx.message.reply(f'The channel __{channel_name}__ is already not managed by Rankie.')
            return

        # Delete the channel from the managed guild list
        if str(ctx.guild.id) in self.__cfg.managed_guilds:
            self.__cfg.managed_guilds[str(ctx.guild.id)].remove(channel.id)

            # If no more entries exist for that guild, remove it.
            if len(self.__cfg.managed_guilds[str(ctx.guild.id)]) <= 0:
                del self.__cfg.managed_guilds[str(ctx.guild.id)]

        await ctx.message.reply(f'The channel __{channel_name}__ will no longer be managed by Rankie.')

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
        if str(channel.id) in self.__cfg.managed_channels:
            # If the message is already managed, throw an error
            if msg.id in self.__cfg.managed_channels[str(channel.id)][1]:
                await ctx.message.reply(f'The message __{msg.id}__ is already being saved by Rankie.')
            else:
                self.__cfg.managed_channels[str(channel.id)][1].append(msg.id)
                await ctx.message.reply(f'The message __{msg.id}__ in __{channel_name}__ will now be saved by Rankie.')

        # Else, the channel is not currently managed...
        else:
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

        # Verify the channel is being managed by Rankie
        if str(channel.id) in self.__cfg.managed_channels:

            # If the message is being saved
            if int(message_id) in self.__cfg.managed_channels[str(channel.id)][1]:
                self.__cfg.managed_channels[str(channel.id)][1].remove(int(message_id))
                await ctx.message.reply(f'The message __{message_id}__ will NO longer be saved by Rankie.')
            
            else:
                await ctx.message.reply(f'The message __{message_id}__ is already not being saved or the passed message ID is invalid.')
        else:
            await ctx.message.reply(f'The channel __{channel_name}__ is not currently managed by Rankie, please ask Rankie to manage this channel before deleting any saved message(s).')

    # Prints a list of all of the currently managed channels to the requested channel
    async def list_managed_channels(self, ctx):
        # Check if the guild has managed channels
        if str(ctx.guild.id) in self.__cfg.managed_guilds:
            msg = f'Managed channels:\n```{"Channel":<20}\t{"Frequency":<20}\n{"-------":<20}\t{"---------":<20}\n'

            for channel_id in self.__cfg.managed_guilds[str(ctx.guild.id)]:
                channel_name = str(discord.utils.get(ctx.message.guild.channels, id=channel_id))
                msg += f'{channel_name:<20}\t{self.__cfg.managed_channels[str(channel_id)][0]:<10}\n'

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

        # If the channel is being managed
        if str(channel.id) in self.__cfg.managed_channels:
            # If the length of saved messages is > 0
            if len(self.__cfg.managed_channels[str(channel.id)][1]) > 0:
                msg = f'Saved message(s) in __{channel_name}__:\n'
                for msg_id in self.__cfg.managed_channels[str(channel.id)][1]:
                    msg += f'``{msg_id}``\n'

                await ctx.message.reply(msg)
            else:
                await ctx.message.reply(f'The channel __{channel_name}__ has no saved messages.')
        else:
            await ctx.message.reply(f'The channel __{channel_name}__ is not currently being managed by Rankie.')