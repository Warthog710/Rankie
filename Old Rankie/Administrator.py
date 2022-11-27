import discord
class administrator:
    def __init__(self, rankie, logging):
        self.__rankie = rankie
        self.__logging = logging

    # Attaches and sends managed_channels to a discord message
    async def get_log_file(self, ctx):
        try:
            await ctx.message.reply(file=discord.File(f'logs/rankie.log'))
        except Exception as e:
            self.__logging.error(f'Failed to deliver logs: {e}')
            await ctx.message.reply(f'Error: {e}')

    async def get_guilds(self, ctx):
        msg = f'Connected to {len(self.__rankie.guilds)} server(s):\n'

        # Iterate over guilds
        for guild in self.__rankie.guilds:
            msg += f'``{guild.name:<20}\t{guild.id:<15}``\n'

        # Send the msg
        await ctx.message.reply(msg)

    