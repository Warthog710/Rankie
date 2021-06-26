# Rankie

#### Description:
Rankie is a Discord bot that is integrated with <a href="https://raider.io/">Raider.io</a>. It allows server owners to create custom roles around IO scores. For example, I can create a role for scores ranging from *0-1000* called *Test*. When a user request to be assigned a role, it will look up the passed character on Raider IO and assign the user the appropriate role. If they qualify for no existing roles, they will be informed of that case.<br><br>
Roles can be customized on a per server basis. Only users with the ability to managed the server can set the roles. In addition, the prefix that Rankie uses on the server can be changed by server managers. By default this is set to *?*.

#### Commands:
 * ``?assignRole``: Given ``<region>/<realm>/<name>``. Assign a role based on their IO score. If no role exists, inform the user of the case.
 * ``?profile``: Given ``<region>/<realm>/<name>``. Return the Raider IO profile url.
 * ``?setRank``:
 * ``?deleteRank``:
 * ``?listRanks``:
 * ``?setPrefix``: