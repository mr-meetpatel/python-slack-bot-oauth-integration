# Oauth Integration of Slack Bot in Python

This repository contains a sample application for implementing OAuth with Slack using the `python-slackclient` and `python-slack-events-api` packages. It has been tested with `python 3.10`.

To facilitate local development of Slack apps, it is recommended to use [`ngrok`](https://ngrok.com/download). If you're not familiar with `ngrok`, you can follow [this guide](https://api.slack.com/tutorials/tunneling-with-ngrok) to set it up.

Before we begin, ensure that you have a development workspace where you have the necessary permissions to install apps. If you don't have a workspace set up, you can [create one](https://slack.com/create). Additionally, you need to [create a new app](https://api.slack.com/apps?new_app=1) if you haven't done so already.

## Installation

First, make sure you have `pipenv` installed. You can install it by running:

```
pip install pipenv
```

Next, install the project dependencies using the following command:
```
pipenv install
```

Activate the virtual environment:
```
pipenv shell
```

## Configuration

This application requires you to set up a few environment variables. Create a new file named `.env` by copying the provided `.env.example` file: 
```
cp .env.example .env
```
Open the `.env` file and provide the following values:
```
SLACK_CLIENT_ID = YOUR_SLACK_CLIENT_ID
SLACK_CLIENT_SECRET = YOUR_SLACK_CLIENT_SECRET
SLACK_SIGNING_SECRET = YOUR_SLACK_SIGNING_SECRET
```

Replace `YOUR_SLACK_CLIENT_ID`, `YOUR_SLACK_CLIENT_SECRET`, and `YOUR_SLACK_SIGNING_SECRET` with the corresponding values from your Slack app configuration.

## Running the Application

Start the application by running the following command:

```
python app.py
```
This will start the application on port `5000`.
Now, let's use `ngrok` to create a publicly accessible URL for the application and set up the necessary URLs for OAuth and event handling.

```
ngrok http 5000
```

`ngrok` will output a forwarding address for both `http` and `https` protocols. Take note of the `https` URL, which should look similar to the following:
```
Forwarding https://your-url.domain -> http://localhost:5000
```

Open your Slack app's configuration page at https://api.slack.com/apps and navigate to the **OAuth & Permissions** section. Under **Redirect URLs**, add your `ngrok` forwarding address with the `/finish_auth` path appended. For example:

```
https://your-url.domain/finish_auth
```

While you're in the **Event Subscriptions** section, add the `member_joined_channel` event, as the app utilizes it to send a direct message.

## Ready to Go!

Everything is set up now. Open your web browser and visit [`http://localhost:5000/begin_auth`](http://localhost:5000/begin_auth) to initiate the OAuth installation flow for your app!

Feel free to explore the code and customize it as needed to build your Slack integration. Happy coding!
Hope this helps!