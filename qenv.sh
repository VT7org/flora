#!/bin/bash

# Script to generate .env file from configuration variables

ENV_FILE=".env"

# Remove existing .env file if it exists
if [ -f "$ENV_FILE" ]; then
    rm "$ENV_FILE"
fi

# Create new .env file
touch "$ENV_FILE"

# Write variables to .env file
cat << EOF > "$ENV_FILE"
# Telegram API credentials from my.telegram.org
API_ID=18136872
API_HASH=312d861b78efcd1b02183b2ab52a83a4

# Bot token from @Botfather
BOT_TOKEN=

# MongoDB URI for database
MONGO_DB_URI=

# Clean mode delete time in minutes
CLEANMODE_MINS=5

# Maximum audio duration for voice chat in minutes
DURATION_LIMIT=5400

# Maximum song download duration in minutes
SONG_DOWNLOAD_DURATION_LIMIT=5400

# Private group ID for logging
LOG_GROUP_ID=-1002030443562

# Owner ID(s)
OWNER_ID=5960968099

# Privacy policy link
PRIVACY_LINK=https://telegra.ph/Privacy-Policy-for-VenomMusic-01-02

# Enable extra plugins (True/False)
EXTRA_PLUGINS=False

# Extra plugins repository
EXTRA_PLUGINS_REPO=https://github.com/VT7org/floraplugins

# Extra plugins folder
EXTRA_PLUGINS_FOLDER=plugins

# Auto leaving assistant (True/False)
AUTO_LEAVING_ASSISTANT=False

# Assistant leave time in seconds
ASSISTANT_LEAVE_TIME=5800

# Heroku API key
HEROKU_API_KEY=

# Heroku app name
HEROKU_APP_NAME=

# Upstream repository
UPSTREAM_REPO=https://github.com/VT7org/flora

# Upstream branch
UPSTREAM_BRANCH=main

# Git token for private repo
GIT_TOKEN=

# Support channel link
SUPPORT_CHANNEL=https://t.me/BillaSpace

# Support group link
SUPPORT_GROUP=https://t.me/BillaCore

# Private bot mode (True/False)
PRIVATE_BOT_MODE=False

# YouTube download sleep time in seconds
YOUTUBE_EDIT_SLEEP=3

# Telegram download sleep time in seconds
TELEGRAM_EDIT_SLEEP=5

# GitHub repository link
GITHUB_REPO=https://github.com/bhootnath/billanath2

# Spotify credentials
SPOTIFY_CLIENT_ID=19609edb1b9f4ed7be0c8c1342039362
SPOTIFY_CLIENT_SECRET=409e31d3ddd64af08cfcc3b0f064fcbe

# Maximum number of video streams
VIDEO_STREAM_LIMIT=999

# Maximum server playlist limit
SERVER_PLAYLIST_LIMIT=10

# Maximum playlist fetch limit
PLAYLIST_FETCH_LIMIT=50

# Telegram audio file size limit in bytes
TG_AUDIO_FILESIZE_LIMIT=1073741824

# Telegram video file size limit in bytes
TG_VIDEO_FILESIZE_LIMIT=1073741824

# Auto-set bot commands (True/False)
SET_CMDS=True

# String sessions (comma-separated)
STRING_SESSIONS=
EOF

echo "Never Forget To fill Necessary Variables which are Empty"
echo " Initial .env file has been created successfully!"
