# Space - Telegram

Simple script for publish amazing space photos to Telegram-channel.

![image](https://user-images.githubusercontent.com/22379662/151451756-f218e37d-e9b7-44ea-90f7-afb39c9a4a6f.png)

The script loads several photos from NASA APOD, NASA EPIC and SpaceX Launch resources. And with a given interval publishes them in the Telegram channel. When the photos run out, the script loads new ones.

## Usages

1. [Generate](https://api.nasa.gov/) NASA API key for Developers.
2. [Register](https://telegram.me/BotFather) a bot in Telegram and get the API-token.
3. Create a Telegram channel and add the bot to administrators. Get the channel ID.
4. Create a file `.env` and put youre key, token and id in it
```
API_KEY_NASA=<youre_api_key>
SPACEPHOTOSBOT_TOKEN=<youre_bot_token>
SPACEPHOTOS_CHANNEL_ID=<youre_channel_id>
```
5. If you want to change the interval between posting photos, you can add the `DELAY` parameter to the `.env` file. This option sets how many seconds between posting a photo. The default value is one day (86400 seconds).
```
DELAY=<time_in_seconds>
```
Run script
```
$python space-telegram.py
```

## How to install

Python3 should be already installed. 
Then use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```

### Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).
