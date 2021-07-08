class help:
    def __init__(self, cfg):
        self.__cfg = cfg

    # Prints a help message for the passed command (or generic) in the requested channel
    async def help_message(self, ctx, cmd):
        prefix = self.__cfg.get_prefix(None, ctx.message)
        cmd = ' '.join(cmd)
        cmd = cmd.upper()

        if 'ASSIGNRANK' == cmd or 'AR' == cmd:
            msg = f'```Assigns a rank based on your current Raider.io mythic+ score.\n\nUsage: {prefix}assignRank <region>/<realm>/<name>\n\nAliases: {prefix}ar\n\nExample: {prefix}assignRank us/aggramar/sapphirre```'
            await ctx.message.reply(msg)
        elif 'PROFILE' == cmd or 'P' == cmd:
            msg = f'```Return the URL for a characters Raider.io profile.\n\nUsage: {prefix}profile <region>/<realm>/<name>\n\nAliases: {prefix}p\n\nExample: {prefix}profile us/aggramar/sapphirre```'
            await ctx.message.reply(msg)
        elif 'LISTRANKS' == cmd or 'LR' == cmd:
            msg = f'```Lists all the currently set ranks for this server.\n\nUsage: {prefix}listRanks\n\nAliases: {prefix}lr```'
            await ctx.message.reply(msg)
        elif ('SETRANK' == cmd or 'SR' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            msg = f'```Adds a rank attached to a specified IO range. When a member asks to be assigned a rank and their mythic+ score is within this range, the associated rank will be assigned.\n\nUsage: {prefix}setRank <IO_Range> [Rank Name]\n\nAliases: {prefix}sr\n\nExample: {prefix}setRank 0-1000 Baby\nExample: {prefix}setRank 1000+ Bigger Baby\n\nNote, the IO range passed or the rank name cannot overlap with existing managed ranks. In addition, the end value of a range is exclusive. This means that the range 0-1000 maxes out at 999.```'
            await ctx.message.reply(msg)
        elif ('DELETERANK' == cmd or 'DR' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            msg = f'```Deletes a rank that already exists.\n\nUsage: {prefix}deleteRank [Rank Name]\n\nAliases: {prefix}dr\n\nExample: {prefix}deleteRank Bigger Baby```'
            await ctx.message.reply(msg)
        elif ('SETPREFIX' == cmd or 'SP' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            msg = f'```Sets the prefix that Rankie uses for this server.\n\nUsage: {prefix}setPrefix <desired_prefix>\n\nAliases: {prefix}sp\n\nExample: {prefix}setPrefix !```'
            await ctx.message.reply(msg)
        elif ('SETSEASON' == cmd or 'SS' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            msg = f'```Sets the current season that will be used to assign ranks.\n\nUsage: {prefix}setSeason <desired_season>\n\nAliases: {prefix}ss\n\nOnly "current" and "previous" are supported as inputs for this command.```'
            await ctx.message.reply(msg)
        elif ('SETMANAGEDCHANNEL' == cmd or 'SMC' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            msg = f'```Sets a channel to be managed. A managed channel will have its messages periodically deleted at a defined frequency. Currently Rankie only supports two frequencies, hourly and daily. Only text channels can be managed.\n\nUsage: {prefix}setManagedChannel <channel_name> <frequency>\n\nAliases: {prefix}smc\n\nExample: {prefix}setManagedChannel general daily```'
            await ctx.message.reply(msg)
        elif ('DELETEMANAGEDCHANNEL' == cmd or 'DMC' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            msg = f'```Removes a managed channel from being managed. This channel will no longer have its messages periodically deleted at the requested frequency.\n\nUsage: {prefix}deleteManagedChannel <channel_name>\n\nAliases: {prefix}dmc\n\nExample: {prefix}deleteManagedChannel general```'
            await ctx.message.reply(msg)
        elif ('SETSAVEDMESSAGE' == cmd or 'SSM' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            msg = f'```Sets a saved message in a managed channel. A saved message will not be deleted when performing channel management.\n\nUsage: {prefix}setSavedMessage <channel_name> <message_id>\n\nAliases: {prefix}ssm\n\nExample: {prefix}setSavedMessage general 862459611819016212```'
            await ctx.message.reply(msg)
        elif ('DELETESAVEDMESSAGE' == cmd or 'DSM' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            msg = f'```Removes a saved message from a managed channel. This message will no longer be saved when performing channel management.\n\nUsage: {prefix}deleteSavedMessage <channel_name> <message_id>\n\nAliases: {prefix}dsm\n\nExample: {prefix}deleteSavedMessage general 862459611819016212```'
            await ctx.message.reply(msg)
        elif ('LISTMANAGEDCHANNELS' == cmd or 'LMC' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            msg = f'```Lists all the current channels being managed by Rankie in this server.\n\nUsage: {prefix}listManagedChannels\n\nAliases: {prefix}lmc```'
            await ctx.message.reply(msg)
        elif ('LISTSAVEDMESSAGES' == cmd or 'LSM' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            msg = f'```Lists all the saved messages for a managed channel in this server.\n\nUsage: {prefix}listSavedMessages <channel_name>\n\nAliases: {prefix}lsm\n\nExample: {prefix}listSavedMessages general```'
            await ctx.message.reply(msg)
        else:
            msg = 'Available Commands:\n```'
            msg += f'{prefix}assignRank <region>/<realm>/<name>\n\n'
            msg += f'{prefix}profile <region>/<realm>/<name>\n\n'
            msg += f'{prefix}listRanks\n\n'

            # If the user has manage_guild permissions, give them info on these commands
            if ctx.message.author.guild_permissions.manage_guild:
                msg += f'{prefix}setRank <IO_Range> [Rank Name]\n\n'
                msg += f'{prefix}deleteRank [Rank Name]\n\n'
                msg += f'{prefix}setPrefix <desired_prefix>\n\n'
                msg += f'{prefix}setSeason <desired_season>\n\n'
                msg += f'{prefix}setManagedChannel <channel_name> <frequency>\n\n'
                msg += f'{prefix}deleteManagedChannel <channel_name>\n\n'
                msg += f'{prefix}setSavedMessage <channel_name> <message_id>\n\n'
                msg += f'{prefix}deleteSavedMessage <channel_name> <message_id>\n\n'
                msg += f'{prefix}listManagedChannels\n\n'
                msg += f'{prefix}listSavedMessages <channel_name>\n\n'
                msg += '```'
            else:
                msg += '```'

            msg += f'\nRankie is currently using the __{self.__cfg.get_season(ctx.guild.id)}__ season to calculate its scores for ranks.\n'
            msg += f'\nFor more information on a command, type ``{prefix}help <command_name>``'
            await ctx.message.reply(msg)