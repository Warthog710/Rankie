# Rankie

#### Description:
Rankie is a Discord bot that is integrated with <a href="https://raider.io/">Raider.io</a>. It allows server owners to create custom roles around IO scores. For example, I can create a role for scores ranging from *0-1000* called *Test*. When a user requests to be assigned a role, it will look up the passed character on Raider IO and assign the user the appropriate role. If they qualify for no existing roles, they will be informed of that case.<br><br>
Roles can be customized on a per server basis. Only users with the ability to manage the server can set the roles. In addition, the prefix that Rankie uses on the server can be changed by server managers. By default this is set to *?*<br><br>
*Rankie requires the permissions **manage roles**, **manage messages**, & **read message history***

**Available Regions:** US, EU, TW, KR, CN<br>
**Available Realms:** <a href="https://worldofwarcraft.com/en-us/game/status/us">Official List</a>

#### Commands:
 * ``?assignRank <region>/<realm>/<name>``:
    * Assigns a rank based on the passed characters current Raider IO score. The ranks used for this command must be set using ``?setRank``.

 * ``?profile <region>/<realm>/<name>``:
    * Displays the Raider IO profile URL for the passed character.

 * ``?listRanks``:
    * Lists all the currently set ranks names and IO ranges. These are displayed in ascending order based on their IO range.

#### Administrator Commands:

 * ``?setRank <IO_Range> [Rank Name]``: 
    * Adds a rank attached to a specified IO range. This rank will be created on the server if it does not exist. If the rank already exists the current existing rank will be used. The *IO_Range* passed can take on two forms, either some range ``0-500`` or infinite range ``500+``. Ranks cannot share the same name or overlap with existing ranks. Please note, the IO_Range passed is exclusive. This means a range of ``0-1000`` will max out at 999.

 * ``?deleteRank [Rank Name]``:
    * Deletes an existing rank. This rank will be removed from the server as well. 

 * ``?setPrefix <desired_prefix>``:
    * Sets the prefix that Rankie uses for this server. This prefix must be a single character.

 * ``?setSeason <desired_season>``:
   * Sets the season that Rankie will use when it queries Raider IO for a score. Only *current* and *previous* are supported.

 * ``?setManagedChannel <channel_name> <frequency>``:
   * Sets a text channel to be managed. A managed channel will have its messages deleted periodically at a defined frequency. Only *hourly* and *daily* are supported frequencies.

 * ``?deleteManagedChannel <channel_name>``:
   * Removes a managed channel from being managed. This channel will no longer have its messages periodically deleted at the previously requested frequency.

 * ``?setSavedMessage <channel_name> <message_id>``:
   * Sets a saved message in a managed channel. A saved message will not be deleted when performing channel management.

 * ``?deleteSavedMessage <channel_name> <message_id>``:
   * Removes a saved message in a managed channel. This message will no longer be saved when performing channel management.

 * ``?listManagedChannels``:
   * Lists all the current channels being managed by Rankie on the server the command originates.

 * ``?listSavedMessages <channel_name>``:
   * Lists all the saved messages for a managed channel on the server the command originates.
#### Running Rankie:
Rankie can be invited to your server by clicking on this link: <a href="https://discord.com/oauth2/authorize?client_id=858460009284894750&scope=bot&permissions=268509184">Rankie</a><br>

If you would like to personally host an instance of Rankie, please see release <a href="https://github.com/Warthog710/Rankie/releases/tag/1.3">v1.3</a>. This release does not require a dedicated PostgreSQL database. It only requires an environment variable called *DISCORD_TOKEN* to be set to your bot token. A token can be obtained through Discord's development portal.<br>

How to set an environment variable:<br>
<a href="https://linuxize.com/post/how-to-set-and-list-environment-variables-in-linux/#persistent-environment-variables">Linux</a><br>
<a href="https://docs.oracle.com/en/database/oracle/machine-learning/oml4r/1.5.1/oread/creating-and-modifying-environment-variables-on-windows.html#GUID-DD6F9982-60D5-48F6-8270-A27EC53807D0">Windows</a>
