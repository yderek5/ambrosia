# Ambrosia Slack bot
## Commands
* `@ambrosia` signup <br />
This will sign you up to participate for the day at 10:30 am everyday the bot will message out random people grouped together and suggest they go eat lunch together.
* `@ambrosia` list <br />
This will list all the members in the channel that are participating.

* At 10:30AM everyday the bot will group members of the slack channel who are participating together for lunch. On Thursday and Friday the bot suggests a random takeout, fast food, or restaurant within about 12 miles of MY office. If you'd like to make it your office you can go to google_maps_api.py you'll see each query with a `location` parameter.<br />
You'll want to replace those two numbers which are longitude and latitude with the location of your office.<br />
I went to https://www.latlong.net/ to find mine.



## Goal of the project
* Get people in the office to eat with people they don't usually work with or talk to very often allowing your team to build better relationships with each other.
