import slack
import os
from flask import Flask, request
from slackeventsapi import SlackEventAdapter
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()
client_id = os.getenv("SLACK_CLIENT_ID")
client_secret = os.getenv("SLACK_CLIENT_SECRET")
signing_secret = os.getenv("SLACK_SIGNING_SECRET")
# Generate Random String
state = str(uuid4())
# Scopes needed for this app
oauth_scope = ", ".join(
    ["chat:write", "channels:read", "channels:join", "channels:manage"]
)

# Create a dictionary to represent a database to store our token
token_database = {}
global_token = ""

app = Flask(__name__)


@app.route("/")
def home():
    return "Hello World"


# Route for Oauth flow
@app.route("/begin_auth", methods=["GET"])
def pre_install():
    return f'<a href="https://slack.com/oauth/v2/authorize?scope={oauth_scope}&client_id={client_id}&state={state}"><img alt=""Add to Slack"" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>'


# Route for Oauth flow to redirect to after user accepts scopes
@app.route("/finish_auth", methods=["GET", "POST"])
def post_install():
    # Retrieve the auth code and state from the request params
    auth_code = request.args["code"]
    received_state = request.args["state"]
    # Token is not required to call the oauth.v2.access method
    client = slack.WebClient()

    # verify state received in params matches state we originally sent in auth request
    if received_state == state:
        # Exchange the authorization code for an access token with Slack
        response = client.oauth_v2_access(
            client_id=client_id, client_secret=client_secret, code=auth_code
        )
    else:
        return "Invalid State"

    # Save the bot token and teamID to a database
    # In our example, we are saving it to dictionary to represent a DB
    teamID = response["team"]["id"]
    token_database[teamID] = response["access_token"]
    # Also save the bot token in a global variable so we don't have to
    # do a database lookup on each WebClient call
    global global_token
    global_token = response["access_token"]

    # See if "channel-create-by-slack-bot" exists. Create it if it doesn't.
    channel_exists()

    # Don't forget to let the user know that auth has succeeded!
    return "Auth complete!"


# verifies if "channel-create-by-slack-bot" already exists
def channel_exists():
    client = slack.WebClient(token=global_token)

    # grab a list of all the channels in a workspace
    clist = client.conversations_list()
    exists = False
    for k in clist["channels"]:
        # look for the channel in the list of existing channels
        if k["name"] == "channel-create-by-slack-bot":
            exists = True
            break
    if exists == False:
        # create the channel since it doesn't exist
        create_channel()


# creates a channel named "channel-create-by-slack-bot"
def create_channel():
    client = slack.WebClient(token=global_token)
    resp = client.conversations_create(name="channel-create-by-slack-bot")


# Bind the Events API route to your existing Flask app by passing the server
# instance as the last param, or with `server=app`.
slack_events_adapter = SlackEventAdapter(signing_secret, "/slack/events", app)


# Create an event listener for "member_joined_channel" events
# Sends a DM to the user who joined the channel
@slack_events_adapter.on("member_joined_channel")
def member_joined_channel(event_data):
    user = event_data["event"]["user"]
    channelid = event_data["event"]["channel"]
    teamID = event_data["team_id"]

    # look up the token in our "database"
    token = token_database[teamID]

    # In case the app doesn't have access to the oAuth Token
    if token is None:
        print("ERROR: Autenticate the App!")
        return
    client = slack.WebClient(token=token)

    # Use conversations.info method to get channel name for DM msg
    info = client.conversations_info(channel=channelid)
    msg = f'Welcome! Thanks for joining {info["channel"]["name"]}'
    client.chat_postMessage(channel=user, text=msg)
    print("Message Send...")


app.run()
