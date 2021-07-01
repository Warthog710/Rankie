# Rankie

#### Description:
Rankie is a Discord bot that is integrated with <a href="https://raider.io/">Raider.io</a>. It allows server owners to create custom roles around IO scores. For example, I can create a role for scores ranging from *0-1000* called *Test*. When a user requests to be assigned a role, it will look up the passed character on Raider IO and assign the user the appropriate role. If they qualify for no existing roles, they will be informed of that case.<br><br>
Roles can be customized on a per server basis. Only users with the ability to manage the server can set the roles. In addition, the prefix that Rankie uses on the server can be changed by server managers. By default this is set to *?*<br><br>
***Rankie requires the ability to create, delete, and assign roles.***

**Available Regions:** US, EU, TW, KR, CN<br>
**Available Realms:** <a href="https://worldofwarcraft.com/en-us/game/status/us">Official List</a>

#### Commands:
 * ``?assignRole <region>/<realm>/<name>``:
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
#### Running Rankie:
Rankie can be added to your server by following this URL: <a href="https://top.gg/bot/858460009284894750">Rankie</a><br><br>
If you would like to personally host an instance of Rankie, you are free to do so! For Rankie to work, a config.json file must be present in a config folder with a Discord bot token. A token can be obtained through Discord's development portal. The contents of the file should look like this:
```
{
    "discordToken": "YOUR_TOKEN_HERE"
}
```
