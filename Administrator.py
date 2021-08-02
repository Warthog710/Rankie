import discord
class administrator:
    def __init__(self, logging):
        self.__logging = logging

    # Attaches and sends managed_channels to a discord message
    async def get_log_file(self, ctx):
        try:
            await ctx.message.reply(file=discord.File(f'logs/rankie.log'))
        except Exception as e:
            self.__logging.error(f'Failed to deliver logs: {e}')
            await ctx.message.reply(f'Error: {e}')