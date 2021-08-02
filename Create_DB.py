import os
import psycopg2

db = psycopg2.connect(os.environ.get('DATABASE_URL'), sslmode='require')

try:
    db_handle = db.cursor()

    # Create prefixes
    db_handle.execute('CREATE TABLE prefixes (guild_id text , prefix varchar);')

    # Create roles
    db_handle.execute('CREATE TABLE roles (guild_id text , rank_id text, range text);')

    # Create season
    db_handle.execute('CREATE TABLE season (guild_id text , season text);')

    # Create managed_guilds
    db_handle.execute('CREATE TABLE managed_guilds (guild_id text, channel_id text, frequency text);')

    # Create managed_channels
    db_handle.execute('CREATE TABLE managed_channels (channel_id text, message_id text);')

    # Commit changes
    db.commit()

    # Close db
    db.close()
except Exception as e:
    print(e)
else:
    print('DB Setup successful!')