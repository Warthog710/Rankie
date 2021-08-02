import logging
import discord
import aiohttp

class rank_management:
    def __init__(self, logging, cfg, db):
        self.__logging = logging
        self.__cfg = cfg
        self.__db = db

        #? The top cap for scores, A mythic+ score can never be greater than 99999 (hopefully)
        self.__max_score = 99999

    # Parses a character string <region>/<realm>/<name>
    def __parse_cmd(self, cmd):
        region, realm, name = cmd[0].split('/')
        return region, realm, name

    # Determines if an IO range is valid
    # False = Invalid, True = Valid
    def __check_IO_range(self, IO_range):
        # The string contains a +
        if '+' in IO_range:
            temp = IO_range.split('+')[0]
            
            # If it is numeric
            if temp.isnumeric():
                if int(temp) >= 0:
                    return True

        # The string contains a -
        elif '-' in IO_range:
            temp_min, temp_max = IO_range.split('-')

            if temp_max.isnumeric() and temp_min.isnumeric():
                if int(temp_min) >= 0:
                    if int(temp_min) < int(temp_max):
                        return True

        # The IO_range is invalid              
        return False

    # Given a valid IO_range, parse into a python range
    def __parse_IO_range(self, IO_range):
        if '+' in IO_range:
            temp = int(IO_range.split('+')[0])
            return range(temp, self.__max_score)

        elif '-' in IO_range:
            temp_min, temp_max = IO_range.split('-')
            return range(int(temp_min), int(temp_max))

    # Determine if a valid IO range overlaps with an existing stored range for the guild
    # False = Overlap exists, True = No overlap
    def __detect_overlap(self, guild_id, IO_range, rank):
        existing_roles = self.__db.get_roles(str(guild_id))

        # If roles exist for this guild
        if len(existing_roles) > 0:
            IO_range = self.__parse_IO_range(IO_range)

            # Determine if a name overlaps
            if rank != None:
                for role in existing_roles:
                    if role[0] == rank.id:
                        return False

            # Determine if a range overlaps
            for role in existing_roles:
                saved_range = self.__parse_IO_range(role[1])
                if max(IO_range) >= min(saved_range) and max(saved_range) >= min(IO_range):
                    return False

            # If no overlap was detected, the range is good.
            return True

        # Else, no roles exist for this guild, no overlap can occur
        else:
            return True

    # Sorting key for sorting ranks
    def __sort_key(self, my_tuple):
        return min(self.__parse_IO_range(my_tuple[1]))

    # Returns a sorted list of ranks
    def __get_sorted_ranks(self, guild_id):
        roles = self.__db.get_roles(str(guild_id))

        # If roles exist for that server
        if len(roles) > 0:
            roles.sort(key=self.__sort_key)
            return roles

        # Return none if no roles exist for that server
        else:
            return None

    def __assign_rank_embed(self, name, realm, rank_name, score_range, profile_url, mythic_plus_score, rank_color):
        embed=discord.Embed(title=f'{name.title()}-{realm.title()}', url=profile_url, description=f'You have been assigned {rank_name}. This rank is for players with a mythic+ score of {score_range}.\n\n', color=rank_color)
        embed.add_field(name='Current Mythic+ Score:', value=mythic_plus_score, inline=True)
        embed.add_field(name='Assigned Rank:', value=rank_name, inline=True)
        embed.set_footer(text='\n\nProvided by Raider.io')
        return embed

    async def __add_role(self, ctx, role, IO_range):
        # Add the role
        try:
            self.__db.set_roles(str(ctx.guild.id), str(role.id), str(IO_range))
        # If an error occurs, log it
        except Exception as e:
            self.__logging.error(f'Failed to add a role: {e}')
            await ctx.message.reply('Failed to add role due to a database error. Please try again later.')
        else:
            await ctx.message.reply(f'Successfully created the rank {role} with an assigned IO range of {IO_range}.') 

    # Queries Raider.io for information related to a provided character
    async def __raider_io_query(self, ctx, region, realm, name):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://raider.io/api/v1/characters/profile?region={region}&realm={realm}&name={name}&fields=mythic_plus_scores_by_season%3A{self.__cfg.get_season(ctx.guild.id)}') as response:
                if response.status == 200:
                    resp_json = await response.json()
                    return resp_json
                elif response.status == 400:
                    await ctx.message.reply(f'The character {region}/{realm}/{name} was not found. Please make sure that character exists.')
                    return None
                else:
                    await ctx.message.reply(f'Raider.io failed to respond. Please try again later.')
                    return None 

    # Assigns a rank to a user based on their character
    async def assign_rank(self, ctx, cmd):
        try:
            region, realm, name = self.__parse_cmd(cmd)
            resp_json = await self.__raider_io_query(ctx, region, realm, name)

            # If none is returned, the character was not found, or the API is down.
            if resp_json == None:
                return
            # Else, grab the current score
            else:
                mythic_score = resp_json['mythic_plus_scores_by_season'][0]['scores']['all']
                profile_url = resp_json['profile_url']

        except Exception as e:
            self.__logging.info(f'Failed to recognize the command for assignRank. Cmd={cmd}: {e}')
            await ctx.message.reply(f'I didn\'t recognize that command. Try asking me: **{self.__cfg.get_prefix(None, ctx.message)}help assignRank**')
            return

        # Get a sorted list of ranks
        try:
            sorted_ranks = self.__get_sorted_ranks(ctx.guild.id)
        except Exception as e:
            self.__logging.error(f'Failed to assign a rank: {e}')
            await ctx.message.reply('Failed to assign a rank due to a database error. Please try again later.')

        # If no ranks exist
        if sorted_ranks == None:
            await ctx.message.reply('No ranks currently exist on this server. Please create some ranks.')
            return

        # Determine if they qualify for a rank
        rank_id = None
        for item in sorted_ranks:
            if int(mythic_score) in self.__parse_IO_range(item[1]):
                rank_id = item[0]
                break

        # Check if the user currently posseses that rank
        if rank_id != None:
            if discord.utils.get(ctx.message.author.roles, id=int(rank_id)) != None:
                await ctx.message.reply('You already possess the correct rank.')
                return

        try:
            # Remove all current managed ranks from the user
            for item in sorted_ranks:
                temp = discord.utils.get(ctx.message.author.roles, id=int(item[0]))

                if temp != None:
                    await ctx.message.author.remove_roles(discord.utils.get(ctx.message.guild.roles, id=int(item[0])))

            # Add new rank
            # If rank_id is none, they don't qualify for anything
            if rank_id == None:
                await ctx.message.reply('You do not currently qualify for any set ranks.')
                return
            else:
                await ctx.message.author.add_roles(discord.utils.get(ctx.message.guild.roles, id=int(rank_id)))
        except Exception as e:
            await ctx.message.reply('Failed to assign the correct rank. This is likely due to a permissions issue. Or the rank no longer exists.')
            self.__logging.warning(f'Failed to delete/assign a new role: {e}')
            return    

        assigned_rank = discord.utils.get(ctx.message.guild.roles, id=int(rank_id))
        await ctx.message.reply(embed=self.__assign_rank_embed(name, realm, str(assigned_rank), str(dict(sorted_ranks)[rank_id]), profile_url, mythic_score, assigned_rank.color))

    # Returns a profile link for the user based on the passed character
    async def profile(self, ctx, cmd):
        try:
            region, realm, name = self.__parse_cmd(cmd)
            resp_json = await self.__raider_io_query(ctx, region, realm, name)

            # if none is returned, the character was not found, or the API is down.
            if resp_json == None:
                return
            else:
                profile_url = resp_json['profile_url']
        except Exception as e:
            self.__logging.info(f'Failed to recognize the command for profile. Cmd={cmd}: {e}')
            await ctx.message.reply(f'I didn\'t recognize that command. Try asking me: **{self.__cfg.get_prefix(None, ctx.message)}help profile**')
            return

        await ctx.message.reply(profile_url)

    # Sets a new rank on the server that Rankie manages
    async def set_rank(self, ctx, IO_range, rank_name):
        rank_name = ' '.join(rank_name)

        # If the rank_name is nothing, return an error
        if len(rank_name) <= 0:
            await ctx.message.reply(f'The name for the rank must be greater than 0 characters.')
            return

        rank = discord.utils.get(ctx.message.guild.roles, name=rank_name)

        # Verify IO_range
        try:
            # Determine if a valid range was sent
            if not self.__check_IO_range(IO_range):
                await ctx.message.reply(f'The IO range {IO_range} is invalid.')
                return

            # Verify the passed IO range does not overlap with an existing saved range
            if not self.__detect_overlap(ctx.guild.id, IO_range, rank):
                await ctx.message.reply(f'The rank or IO range passed already exists.')
                return
        except Exception as e:
            self.__logging.info(f'Failed to recognize the command for add_role. role={rank} IO_range={IO_range}: {e}')
            await ctx.message.reply(f'I didn\'t recognize that command. Try asking me: **{self.__cfg.get_prefix(None, ctx.message)}help setRank**')
            return

        # If check for dupe is false, the role does not exist
        if rank == None:
            # Attemp to create the role
            try:
                rank = await ctx.guild.create_role(name=rank_name)
            except Exception as e:
                self.__logging.warning(f'Failed to create a new rank in setRank: {e}')
                await ctx.message.reply('Failed to create the requested rank. This is likely due to a permissions issue. Please make sure Rankie has the ability to create roles or manually create the role before setting the rank.')
                return

        # Add the role
        await self.__add_role(ctx, rank, IO_range)

    # Deletes a managed rank from Rankie and the server
    async def delete_rank(self, ctx, rank_name):
        rank_name = ' '.join(rank_name)

        try:
            roles = self.__db.get_roles(str(ctx.guild.id))
        except Exception as e:
            self.__logging.error(f'Failed to delete a rank: {e}')
            await ctx.message.reply('Failed to delete rank due to a database error. Please try again later.')

        # If the guild ID does not exist in roles, no ranks can be deleted since none have been sent
        if len(roles) <= 0:
            await ctx.message.reply(f'No ranks exist for this server. Before deleting a rank you must create it.')
            return

        # If the role ID does not exist on the server
        rank = discord.utils.get(ctx.message.guild.roles, name=rank_name)
        if rank == None:
            # ? It may be possible that the passed rank has been deleted manually from the guild, in this case NONE would be returned.
            # Iterate through set ranks, if one returns none remove it.
            for rank_id in roles:
                rank = discord.utils.get(ctx.message.guild.roles, id=int(rank_id[0]))

                # One of the saved ranks no longer exists, remove it and state the rank has been deleted.
                if rank == None:
                    try:
                        self.__db.del_role(str(ctx.guild.id), str(rank_id[0]))
                    except Exception as e:
                        self.__logging.error(f'Failed to delete a rank: {e}')
                        await ctx.message.reply('Failed to delete rank due to a database error. Please try again later.')
                        return
                    else:
                        await ctx.message.reply(f'Successfully deleted the rank {rank_name}.')
                        return

            # If no ranks saved return none, state so...        
            await ctx.message.reply('I could not find the passed rank on this server. Please verify the rank exists.')
            return

        # Delete the rank
        try:
            self.__db.del_role(str(ctx.guild.id), str(rank.id))
        except Exception as e:
            self.__logging.error(f'Failed to delete a rank: {e}')
            await ctx.message.reply('Failed to delete rank due to a database error. Please try again later.')
            return

        # Attempt to delete the rank from the server
        try:
            await rank.delete()
        except Exception as e:
            self.__logging.warning(f'Failed to delete a rank in deleteRank: {e}')
            await ctx.message.reply(f'Successfully deleted the rank {rank_name} internally. However, failed to delete the role on the server. This is likely a permissions issue. Please make sure Rankie has the ability to delete roles or manually delete the role.')
            return

        await ctx.message.reply(f'Successfully deleted the rank {rank_name}.')

    # Prints a message containing all the ranks for that server in the requested channel
    async def list_ranks(self, ctx):
        try:
            sorted_ranks = self.__get_sorted_ranks(ctx.guild.id)
        except Exception as e:
            self.__logging.error(f'Failed to list ranks: {e}')
            await ctx.message.reply('Failed to list ranks due to a database error. Please try again later.')
            return

        if sorted_ranks != None:
            if len(sorted_ranks) > 0:
                embed=discord.Embed(title='Currently set ranks:')

                rank_names = ''
                score_ranges = ''
                for item in sorted_ranks:
                    name = str(discord.utils.get(ctx.message.guild.roles, id=int(item[0])))

                    # If the name is None, don't print it and remove that rank
                    if name == 'None':
                        try:
                            self.__db.del_role(str(ctx.guild.id), item[0])

                            # If that was the last rank, return
                            if len(self.__db.get_roles(str(ctx.guild.id))) <= 0:
                                await ctx.message.reply(f'I could not find any set ranks for this server. Please try setting a rank before using this command.')
                                return
                        except Exception as e:
                            self.__logging.error(f'Failed to delete a none rank in list ranks: {e}')

                        continue

                    rank_names += name + '\n'
                    score_ranges += item[1] + '\n'

                embed.add_field(name=f'Ranks:     ', value=rank_names, inline=True)
                embed.add_field(name=f'Ranges:', value=score_ranges, inline=True)
                await ctx.message.reply(embed=embed)
                return

        self.__logging.info(f'Failed to find any roles in listRanks for guild {ctx.guild.id}')
        await ctx.message.reply(f'I could not find any set ranks for this server. Please try setting a rank before using this command.')

    # Sets the season that Rankie uses when determining a characters mythic+ score
    async def set_season(self, ctx, desired_season):
        desired_season = str(desired_season).lower()

        try:
            if desired_season == 'current':
                self.__db.set_season(str(ctx.guild.id), 'current')
                await ctx.message.reply('The __current__ season will now be used for scores.')

            elif desired_season == 'previous':
                self.__db.set_season(str(ctx.guild.id), 'previous')
                await ctx.message.reply('The __previous__ season will now be used for scores.')

            else:
                await ctx.message.reply(f'I didn\'t recognize that command. Try asking me: **{self.__cfg.get_prefix(None, ctx.message)}help setSeason**')
        except Exception as e:
            self.__logging.error(f'Failed to set season: {e}')
            await ctx.message.reply('Failed to set season due to a database error. Please try again later.')
