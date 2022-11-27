import os
import psycopg2

class rankie_db:
    def __init__(self):
        self.__db = psycopg2.connect(os.environ.get('DATABASE_URL'), sslmode='require')

    def get_prefix(self, guild_id):
        query = 'SELECT prefix FROM prefixes WHERE guild_id=%s;'

        # Perform query
        db_handle = self.__db.cursor()
        db_handle.execute(query, (guild_id,))

        # Get result(s)
        result = db_handle.fetchone()

        # Close connection
        db_handle.close()

        # Return result
        return result

    def get_roles(self, guild_id):
        query = 'SELECT rank_id, range FROM roles WHERE guild_id=%s;'

        # Perform query
        db_handle = self.__db.cursor()
        db_handle.execute(query, (guild_id,))

        # Get result(s)
        result = db_handle.fetchall()

        # Close connection
        db_handle.close()

        # Return result
        return result

    def update_role(self, guild_id, rank_id, IO_range):
        query = 'UPDATE roles SET range=%s WHERE guild_id=%s AND rank_id=%s;'

        # Perform query
        db_handle = self.__db.cursor()
        db_handle.execute(query, (IO_range, str(guild_id), str(rank_id),))

        # Close connection
        db_handle.close()

    def get_season(self, guild_id):
        query = 'SELECT season FROM season WHERE guild_id=%s;'

        # Perform query
        db_handle = self.__db.cursor()
        db_handle.execute(query, (guild_id,))

        # Get result(s)
        result = db_handle.fetchone()

        # Close connection
        db_handle.close()

        # Return result
        return result

    def get_managed_channels_for_guild(self, guild_id):
        query = 'SELECT channel_id, frequency FROM managed_guilds WHERE guild_id=%s;'

        # Perform query
        db_handle = self.__db.cursor()
        db_handle.execute(query, (guild_id,))

        # Get result(s)
        result = db_handle.fetchall()

        # Close connection
        db_handle.close()

        # Return result
        return result

    def get_all_managed_channels(self):
        query = 'SELECT channel_id, frequency FROM managed_guilds;'

        # Perform query
        db_handle = self.__db.cursor()
        db_handle.execute(query)

        # Get results
        result = db_handle.fetchall()

        # Close connection
        db_handle.close()

        # Return result
        return result

    def get_saved_messages_for_channel(self, channel_id):
        query = 'SELECT message_id FROM managed_channels WHERE channel_id=%s;'

        # Perform query
        db_handle = self.__db.cursor()
        db_handle.execute(query, (channel_id,))

        # Get result(s)
        result = db_handle.fetchall()

        # Close connection
        db_handle.close()

        # Return result
        return result

    def set_prefix(self, guild_id, prefix):
        # If none no prefix has been set
        if self.get_prefix(guild_id) == None:
            query = 'INSERT INTO prefixes (guild_id, prefix) VALUES (%s, %s);'
            args = (guild_id, prefix,)
        # An existing prefix is present, update the existing value
        else:
            query = 'UPDATE prefixes SET prefix=%s WHERE guild_id=%s;'
            args = (prefix, guild_id,)

        # Perform query
        db_handle = self.__db.cursor()
        db_handle.execute(query, args)

        # Commit results
        self.__db.commit()

        # Close connection
        db_handle.close()

    #? Dumb function, does not detect for dupes, this is done by Rankie before setting a role
    def set_roles(self, guild_id, rank_id, rank_range):
        query = 'INSERT INTO roles (guild_id, rank_id, range) VALUES (%s, %s, %s);'

        # Perform query
        db_handle = self.__db.cursor()
        db_handle.execute(query, (guild_id, rank_id, rank_range,))

        # Commit results
        self.__db.commit()

        # Close connection
        db_handle.close()

    def set_season(self, guild_id, season):
        # If none no season has been set
        if self.get_season(guild_id) == None:
            query = 'INSERT INTO season (guild_id, season) VALUES (%s, %s);'
            args = (guild_id, season,)
        # An existing season is present, update the existing value
        else:
            query = 'UPDATE season SET season=%s WHERE guild_id=%s;'
            args = (season, guild_id,)

        # Perform query
        db_handle = self.__db.cursor()
        db_handle.execute(query, args)

        # Commit results
        self.__db.commit()

        # Close connection
        db_handle.close()

    #? Dumb function, does not detect for dupes, this is done by Rankie before setting a role
    def set_managed_channel_for_guild(self, guild_id, channel_id, frequency):
        query = 'INSERT INTO managed_guilds (guild_id, channel_id, frequency) VALUES (%s, %s, %s);'

        # Perform query
        db_handle = self.__db.cursor()
        db_handle.execute(query, (guild_id, channel_id, frequency,))

        # Commit results
        self.__db.commit()

        # Close connection
        db_handle.close()

    def set_saved_message_for_guild(self, channel_id, message_id):
        query = 'INSERT INTO managed_channels (channel_id, message_id) VALUES (%s, %s);'

        # Perform query
        db_handle = self.__db.cursor()
        db_handle.execute(query, (channel_id, message_id,))

        # Commit results
        self.__db.commit()

        # Close connection
        db_handle.close()

    def del_role(self, guild_id, rank_id):
        query = 'DELETE FROM roles WHERE guild_id=%s AND rank_id=%s;'

        # Perform query
        db_handle = self.__db.cursor()
        db_handle.execute(query, (guild_id, rank_id,))

        # Commit results
        self.__db.commit()

        # Close connection
        db_handle.close()

    def del_managed_channel_from_guild(self, guild_id, channel_id):
        query = 'DELETE FROM managed_guilds WHERE guild_id=%s AND channel_id=%s;'

        # Perform query
        db_handle = self.__db.cursor()
        db_handle.execute(query, (guild_id, channel_id,))

        # Commit results
        self.__db.commit()

        # Close connection
        db_handle.close()

    def del_all_saved_messages_from_channel(self, channel_id):
        query = 'DELETE FROM managed_channels WHERE channel_id=%s;'

        # Perform query
        db_handle = self.__db.cursor()
        db_handle.execute(query, (channel_id,))

        # Commit results
        self.__db.commit()

        # Close connection
        db_handle.close()
    
    def del_all_managed_channels_from_guild(self, guild_id):
        query = 'DELETE FROM managed_guilds WHERE guild_id=%s;'

        # Perform query
        db_handle = self.__db.cursor()
        db_handle.execute(query, (guild_id,))

        # Commit results
        self.__db.commit()

        # Close connection
        db_handle.close()     

    def del_saved_message_from_channel(self, channel_id, message_id):
        query = 'DELETE FROM managed_channels WHERE channel_id=%s AND message_id=%s;'

        # Perform query
        db_handle = self.__db.cursor()
        db_handle.execute(query, (channel_id, message_id,))

        # Commit results
        self.__db.commit()

        # Close connection
        db_handle.close()

    def del_prefix(self, guild_id):
        query = 'DELETE FROM prefixes WHERE guild_id=%s;'

        # Perform query
        db_handle = self.__db.cursor()
        db_handle.execute(query, (guild_id,))

        # Commit results
        self.__db.commit()

        # Close connection
        db_handle.close()

    def del_all_roles_for_guild(self, guild_id):
        query = 'DELETE FROM roles WHERE guild_id=%s;'

        # Perform query
        db_handle = self.__db.cursor()
        db_handle.execute(query, (guild_id,))

        # Commit results
        self.__db.commit()

        # Close connection
        db_handle.close()

    def del_season(self, guild_id):
        query = 'DELETE FROM season WHERE guild_id=%s;'

        # Perform query
        db_handle = self.__db.cursor()
        db_handle.execute(query, (guild_id,))

        # Commit results
        self.__db.commit()

        # Close connection
        db_handle.close()       

    def close_db(self):
        self.__db.close()
