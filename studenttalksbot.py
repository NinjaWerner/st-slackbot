import os
import time
from datetime import datetime as dt
from datetime import date
import re
from slackclient import SlackClient
from slacker import Slacker
from random import randint


# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
slack = Slacker(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = ""
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
help_text = 'You can ask if I a user is an admin with "Is _user_ an admin?" '



def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
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

'''
    COMMANDS
'''


def MondayTeamDay(): # Function is called monday morning at 7:00
    text2 = 'Monday is team day and you are the chosen one! Submit a question here and I will send it to the whole group and collect their responses.'

    ims = slack.im.list().body['ims']
    user_and_im = {}
    user_list = []
    for im in ims: #fills dictionary with {user: direct message id}
        if im['user'] != 'USLACKBOT':
            user_list.append(im['user'])
            user_and_im[im['user']] = im['id']

    rand_int = randint(0,len(user_and_im)-1) #Random integer
    chosen_user = user_list[0] #CHANGE 0 TO rand_int
    for userr in user_list:
        slack.im.open(user = userr) # Open DM channel if user does not have one
    slack_client.api_call("chat.postMessage", channel = user_and_im[chosen_user],text = text2)

    wait_for_response = True
    while wait_for_response:
        command, channel = parse_bot_commands(slack_client.rtm_read())
        if command and channel == user_and_im[chosen_user]:
            text3 = 'Monday is team day. A random person has been chosen to ask the core a question. The question asked was: '
            text4 = ' Please write your answer below.'
            k = text3 + command + text4
            for user in user_list:
                print(user)
                slack_client.api_call("chat.postMessage", channel = user_and_im[user],text = k)

            wait_for_response = False
        time.sleep(RTM_READ_DELAY)









def is_admin_(split_command): #See main 1

    users = slack.users.list()
    users = users.body['members']


    for user_data in users:
        for word in split_command:
            if user_data['name'] == word:
                if user_data['is_admin'] == True:
                    return word + ' is an admin!'
                else:
                    return word + ' is not an admin! :('
    return 'I do not recognize that user! :('



def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Write 'help' to see what I can do! :D."
    command = command.lower()
    # Finds and executes the given command, filling in response
    response = None
    if command == 'help':
        response = help_text
    # This is where you start to implement more commands!
    if command.startswith('do'):
        response = "I can't do much yet"

    if command.startswith('is') and 'admin' in command and '?' in command:
        split_command = command.split(' ')
        response = is_admin_(split_command)

    if command.startswith('test'):
        MondayTeamDay()
    # Sends the response back to the channel
    slack_client.api_call("chat.postMessage",channel=channel,text=response or default_response)


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("StudentTalksBot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)

            if 70000000000 < int(dt.now().strftime('%H%M%S%f')) < 70001000000 and date.today().weekday == 0:
                MondayTeamDay()
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed.")
