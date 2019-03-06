import os
import time
import re
import datetime
import random
import json
from googleplaces import GooglePlaces, types
from slackclient import SlackClient

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_USER_TOKEN'))
slack_api = SlackClient(os.environ.get("SLACK_BOT_TOKEN"))
google_places = GooglePlaces(os.environ.get('GOOGLE_MAPS_KEY'))
# ambrosia's user ID in Slack: value is assigned after the bot starts up
ambrosia_id = None

# constants
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
PARTICIPATE_COMMAND = "eat"
SHOW_PARTICIPANTS_COMMAND = "list"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
TIME = datetime.datetime
MEMBERS = []
PLACES = []


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == ambrosia_id:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def register_user_as_participating(channel):
    # need to capture the user who sent the message and put them inside an array
    messages = slack_api.api_call(
        "channels.history",
        channel=channel,
    )['messages']
    # capture the id of the user who issued a command
    id_of_user = messages[0]['user']
    # search for the users name instead of id
    list_of_members = slack_client.api_call("users.list")["members"]
    for member in list_of_members:
        if member['id'] == id_of_user:
            user = member['name']
            global MEMBERS
            MEMBERS.append(f"<@{user}>")
            MEMBERS = list(set(MEMBERS))
            response = slack_client.api_call(
                "chat.postMessage",
                channel=channel,
                text=f"Thanks <@{user}>! You are now signed up to become a lunch buddy today.",
            )
            return response


def print_participating_users(channel):
    global MEMBERS
    members = ""
    for member in MEMBERS:
        members += f"{member} \n"

    message = json.dumps([{"text": f"{members}",
                           "color": "#3AA3E3", "attachment_type": "default"}])

    response = slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text="All the participating members are:",
        attachments=message
    )
    return response


def build_message(group):
    text = ""
    for user in group:
        text += f"{user}, "
    if datetime.datetime.now().isoweekday() == 4 or 5:
        # here is google maps api logic to randomly select a restaurant if the day is thursday or friday
        takeout = google_places.nearby_search(
            location='Fairway, KS, United States',
            radius=20000, types=[types.TYPE_MEAL_TAKEAWAY])

        restaurants = google_places.nearby_search(
            location="Fairway, KS, United States",
            radius=20000, types=[types.TYPE_RESTAURANT]
        )

        fast_food = google_places.nearby_search(
            location="Fairway, KS, United States", keyword="fast food",
            radius=20000, types=[types.TYPE_FOOD]
        )
        random_takeout = takeout.places
        random_restaurant = restaurants.places
        random_fast_food = fast_food.places

        random.shuffle(random_takeout)
        random.shuffle(random_restaurant)
        random.shuffle(random_fast_food)

        PLACES.append(random_takeout[0].name)
        PLACES.append(random_restaurant[0].name)
        PLACES.append(random_fast_food[0].name)

        random.shuffle(PLACES)

        text += f"I recommend going here {PLACES[0]}"
    message = json.dumps([{"text": f"{text}",
                           "color": "#3AA3E3", "attachment_type": "default"}])
    return message


def create_groups_and_send_messages():
    global MEMBERS
    random.shuffle(MEMBERS)
    # this function should manipulate the global members array by removing four at a time
    # and printing them in a message at 11am
    # see if the len(MEMBERS) is even or odd if odd make a group of 3 first then make groups of four
    # pull the first 3 or 4 people from MEMBERS and pass them into GROUP

    x = True
    while x is True:
        if len(MEMBERS) < 2:
            print("NO MORE OR NOT ENOUGH PEOPLE SIGNED UP")
            break
        else:
            if len(MEMBERS) & 1:
                first_three = MEMBERS[:3]
                MEMBERS = MEMBERS[3:]
                print(build_message(first_three))
                slack_client.api_call(
                    "chat.postMessage",
                    channel="testing-slack-bot",
                    attachments=build_message(first_three)
                )
            else:
                first_four = MEMBERS[:4]
                MEMBERS = MEMBERS[4:]
                print(build_message(first_four))
                slack_client.api_call(
                    "chat.postMessage",
                    channel="testing-slack-bot",
                    attachments=build_message(first_four)
                )


def handle_command(command, channel):
    # Executes bot command if the command is known
    default_response = f"Not sure what you mean. Try `@ambrosia` *{PARTICIPATE_COMMAND}* or `@ambrosia` *{SHOW_PARTICIPANTS_COMMAND}*."
    # Finds and executes the given command, filling in response
    if command.startswith(PARTICIPATE_COMMAND):
        register_user_as_participating(channel)

    if command.startswith(SHOW_PARTICIPANTS_COMMAND):
        print_participating_users(channel)

    if not command.startswith(PARTICIPATE_COMMAND) and not command.startswith(SHOW_PARTICIPANTS_COMMAND):
        print(default_response)
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=default_response
        )


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Ambrosia is connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        ambrosia_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
            HOUR = TIME.now().hour
            MINUTE = TIME.now().minute
            SECOND = TIME.now().second
            if HOUR is 10 and MINUTE is 30 and SECOND is 0:
                print('The time is 10:30! Grouping users...')
                slack_client.api_call(
                    "chat.postMessage",
                    channel="testing-slack-bot",
                    text="Okay, Here's the lunch groups for today!"
                )
                create_groups_and_send_messages()
    else:
        print("Connection failed. Exception traceback printed above.")
