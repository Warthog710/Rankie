from discord import Embed
class help:
    def __init__(self, cfg):
        self.__cfg = cfg

    def help_embed(self, title, description, usage, aliases, example):
        embed = Embed(title=title, description=description)
        embed.add_field(name='Usage:', value=usage, inline=False)
        embed.add_field(name='Aliases:', value=aliases, inline=False)
        embed.add_field(name='Example:', value=example, inline=False)
        return embed

    # Prints a help message for the passed command (or generic) in the requested channel
    async def help_message(self, ctx, cmd):
        prefix = self.__cfg.get_prefix(None, ctx.message)
        cmd = ' '.join(cmd)
        cmd = cmd.upper()

        if 'ASSIGNRANK' == cmd or 'AR' == cmd:
            title = f'{prefix}assignRank'
            description = 'Assigns a rank based on your current Raider.io mythic+ score. For this command to work the user must provide the region, realm, and character name. This characters current mythic+ score will be used during rank calculation.\n\nSupported regions: ***US, EU, TW, KR, CN***'
            usage = f'{prefix}assignRank *region*/*realm*/*name*'
            aliases = f'{prefix}ar'
            example = f'{prefix}assignRank us/aggramar/sapphirre'

            # Send embed
            await ctx.message.reply(embed=self.help_embed(title, description, usage, aliases, example))
        elif 'PROFILE' == cmd or 'P' == cmd:
            title = f'{prefix}profile'
            description = 'Returns the URL for a characters Raider.io profile.'
            usage = f'{prefix}profile *region*/*realm*/*name*'
            aliases = f'{prefix}p'
            example = f'{prefix}profile us/aggramar/sapphirre'

            # Send embed
            await ctx.message.reply(embed=self.help_embed(title, description, usage, aliases, example))
        elif 'LISTRANKS' == cmd or 'LR' == cmd:
            title = f'{prefix}listRanks'
            description = 'Lists all the currently set ranks for this server.'
            usage = f'{prefix}listRanks'
            aliases = f'{prefix}lr'
            example = f'{prefix}listRanks'

            # Send embed
            await ctx.message.reply(embed=self.help_embed(title, description, usage, aliases, example))        
        elif ('SETRANK' == cmd or 'SR' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            title = f'{prefix}setRank'
            description = 'Adds a rank attached to a specified mythic+ score range. When a member asks to be assigned a rank and their mythic+ score is within this range, the associated rank will be assigned. Note, the mythic+ score range passed cannot overlap with an existing managed rank. In addition, the end value of a range is exclusive. This means that the range 0-1000 maxes out at 999.'
            usage = f'{prefix}setRank *IO_Range* *Rank Name*'
            aliases = f'{prefix}sr'
            example = f'{prefix}setRank 0-1000 Baby\n{prefix}setRank 1000+ Bigger Baby'
            
            # Send embed
            await ctx.message.reply(embed=self.help_embed(title, description, usage, aliases, example))
        elif ('MODIFYRANK' == cmd or 'MR' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            title = f'{prefix}modifyRank'
            description = 'Modifies an existing rank with a new mythic+ score range.'
            usage = f'{prefix}modifyRank *IO_Range* *Rank Name*'
            aliases = f'{prefix}mr'
            example = f'{prefix}modifyRank 0-500 Baby\n{prefix}modifyRank 500+ Bigger Baby'

            # Send embed
            await ctx.message.reply(embed=self.help_embed(title, description, usage, aliases, example))  
        elif ('DELETERANK' == cmd or 'DR' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            title = f'{prefix}deleteRank'
            description = 'Deletes a rank that is currently being managed. This rank will also be deleted from the server. Note, if the rank does not exist, Rankie will also fail to delete the rank internally.'
            usage = f'{prefix}deleteRank *Rank Name*'
            aliases = f'{prefix}dr'
            example = f'{prefix}deleteRank Bigger Baby'

            # Send embed
            await ctx.message.reply(embed=self.help_embed(title, description, usage, aliases, example))  
        elif ('SETPREFIX' == cmd or 'SP' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            title = f'{prefix}setPrefix'
            description = 'Sets the prefix that Rankie uses for this server. Prefixes must be a single character.'
            usage = f'{prefix}setPrefix *desired_prefix*'
            aliases = f'{prefix}sp'
            example = f'{prefix}setPrefix !'

            # Send embed
            await ctx.message.reply(embed=self.help_embed(title, description, usage, aliases, example))  
        elif ('SETSEASON' == cmd or 'SS' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            title = f'{prefix}setSeason'
            description = 'Sets the season that Rankie will use to assign ranks. This can be either *current* or *previous*.'
            usage = f'{prefix}setSeason *desired_season*'
            aliases = f'{prefix}ss'
            example = f'{prefix}setSeason current'

            # Send embed
            await ctx.message.reply(embed=self.help_embed(title, description, usage, aliases, example))  
        elif ('SETMANAGEDCHANNEL' == cmd or 'SMC' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            title = f'{prefix}setManagedChannel'
            description = 'Sets a channel to be managed. A managed channel will have its messages periodically deleted at a defined frequency. Currently Rankie only supports two frequencies, *hourly* and *daily*. Only text channels can be managed.'
            usage = f'{prefix}setManagedChannel *channel_name* *frequency*'
            aliases = f'{prefix}smc'
            example = f'{prefix}setManagedChannel general daily'

            # Send embed
            await ctx.message.reply(embed=self.help_embed(title, description, usage, aliases, example))  
        elif ('DELETEMANAGEDCHANNEL' == cmd or 'DMC' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            title = f'{prefix}deleteManagedChannel'
            description = 'Removes a managed channel from being managed. This channel will no longer have its messages periodically deleted at the requested frequency. Note, the actual channel is not deleted from the server.'
            usage = f'{prefix}deleteManagedChannel *channel_name*'
            aliases = f'{prefix}dmc'
            example = f'{prefix}deleteManagedChannel general'

            # Send embed
            await ctx.message.reply(embed=self.help_embed(title, description, usage, aliases, example))
        elif ('SETSAVEDMESSAGE' == cmd or 'SSM' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            title = f'{prefix}setSavedMessage'
            description = 'Sets a saved message in a managed channel. A saved message will not be deleted when performing channel management.'
            usage = f'{prefix}setSavedMessage *channel_name* *message_id*'
            aliases = f'{prefix}ssm'
            example = f'{prefix}setSavedMessage general 862459611819016212'

            # Send embed
            await ctx.message.reply(embed=self.help_embed(title, description, usage, aliases, example))
        elif ('DELETESAVEDMESSAGE' == cmd or 'DSM' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            title = f'{prefix}deleteSavedMessage'
            description = 'Removes a saved message from a managed channel. This message will no longer be saved when performing channel management. Note, this message will not be immediately deleted, rather it will be deleted when Rankie performs its next scheduled channel management.'
            usage = f'{prefix}deleteSavedMessage *channel_name* *message_id*'
            aliases = f'{prefix}dsm'
            example = f'{prefix}deleteSavedMessage general 862459611819016212'

            # Send embed
            await ctx.message.reply(embed=self.help_embed(title, description, usage, aliases, example))
        elif ('LISTMANAGEDCHANNELS' == cmd or 'LMC' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            title = f'{prefix}listManagedChannels'
            description = 'Lists all the current channels being managed by Rankie in this server.'
            usage = f'{prefix}listManagedChannels'
            aliases = f'{prefix}lmc'
            example = f'{prefix}listManagedChannels'

            # Send embed
            await ctx.message.reply(embed=self.help_embed(title, description, usage, aliases, example))
        elif ('LISTSAVEDMESSAGES' == cmd or 'LSM' == cmd) and ctx.message.author.guild_permissions.manage_guild:
            title = f'{prefix}listSavedMessages'
            description = 'Lists all the saved messages for a managed channel in this server.'
            usage = f'{prefix}listSavedMesages *channel_name*'
            aliases = f'{prefix}lsm'
            example = f'{prefix}listSavedMessages general'

            # Send embed
            await ctx.message.reply(embed=self.help_embed(title, description, usage, aliases, example))
        else:
            embed = Embed(title='Rankie Help', description=f'For more information on a command type: {prefix}help *command_name*')
            msg = f'{prefix}assignRank *region*/*realm*/*name*\n\n'
            msg += f'{prefix}profile *region*/*realm*/*name*\n\n'
            msg += f'{prefix}listRanks\n\n'

            # If the user has manage_guild permissions, give them info on these commands
            if ctx.message.author.guild_permissions.manage_guild:
                msg += f'{prefix}setRank *IO_Range* *Rank Name*\n\n'
                msg += f'{prefix}modifyRank *IO_Range* *Ranke Name*\n\n'
                msg += f'{prefix}deleteRank *Rank Name*\n\n'
                msg += f'{prefix}setPrefix *desired_prefix*\n\n'
                msg += f'{prefix}setSeason *desired_season*\n\n'
                msg += f'{prefix}setManagedChannel *channel_name* *frequency*\n\n'
                msg += f'{prefix}deleteManagedChannel *channel_name*\n\n'
                msg += f'{prefix}setSavedMessage *channel_name* *message_id*\n\n'
                msg += f'{prefix}deleteSavedMessage *channel_name* *message_id*\n\n'
                msg += f'{prefix}listManagedChannels\n\n'
                msg += f'{prefix}listSavedMessages *channel_name*\n\n'

            embed.add_field(name='Available Commands:', value=msg, inline=False)
            embed.add_field(name='Info:', value=f'Rankie is currently using the __{self.__cfg.get_season(ctx.guild.id)}__ season to calculate its scores for ranks.')

            await ctx.message.reply(embed=embed)