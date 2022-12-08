# ShowCaseSoT---Public
 NightBot API Consumer to update Sea of Thieves Season 8 PvP Stats, running as OBS Script

# WTF is this?
OBS Studio features its own Python Module to allow scripts to access its functionality directly. This plugin builds on that module.
Using the Sea of Thieves profile page, it will automatically retrieve (at its current state) your Reaper PvP Faction Wins and Level.
It will then use that information to change a Nightbot command on your Twitch channel. 

# How do to install?
OBS does not have a native Python Interpreter. Hence, you're gonna have to install Python and the other requirements below:

Python 3.10<br>
Python Requests<br>
Python Selenium<br>

Find help to install these online. After installing, you'll have to provide the installation path of Python to OBS Studio.
Keep in mind that the only binary used for this project, chromedriver, is provided in this repository,
but can also be downloaded from their official source online (Version 108).
