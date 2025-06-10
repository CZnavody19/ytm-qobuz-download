# YouTube Music downloader

This is a relatively simple script that grabs all songs form a YouTube Music playlist and attempts to find them on Qobuz and download them in high-res.

## Setup instructions
1. Have Python and pip
2. Install the requirements using `pip install -r requirements.txt`
3. Set the required secrets as per the [example env](.env.example)
4. Make sure you have the `oauth.json` file present
5. Run using `python3 main.py` or set up a cronjob

## Getting the required tokens
1. Get the OAuth credentials for YouTube Music using [this guide](https://ytmusicapi.readthedocs.io/en/stable/setup/oauth.html)
2. Get your Qobuz `USER_ID`, `TOKEN`, `APP_ID` and `APP_SECRET`
3. Create the playlist and get the id (found in the URL)

### Plex refresh
1. Get your token using [this guide](https://www.plexopedia.com/plex-media-server/general/plex-token/#getcurrentusertoken)
2. Get the library id using [this](https://plexapi.dev/api-reference/library/get-all-libraries)

### Discord notifications
1. Create a webhook in a Discord channel
2. Paste the URL to the env file

###### for new tokens the `APP_ID` will be `798273057` and `APP_SECRET` will be `abb21364945c0583309667d13ca3d93a`

## Features:
- [x] Qobuz search
- [ ] Deezer search
- [x] Dynamic threshold and weight setup (need to edit the [finder.py](finder.py) file)
- [x] Storing already downloaded tracks
- [x] Plex refresh
- [x] Discord notifications

Deezer search and download is planned after [this issue](https://github.com/nathom/streamrip/issues/846) is fixed

###### NOTE: The APIs used are unofficial and im not responsible for the usage, use at your own risk blah blah ...

###### ANOTHER NOTE: This breaks sometimes, mostly due to the unofficial APIs and their changes