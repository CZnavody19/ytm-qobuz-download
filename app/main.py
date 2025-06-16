from typing import Any
from ytmusicapi import YTMusic, OAuthCredentials
from dotenv import load_dotenv
from streamrip.client import QobuzClient
from streamrip.config import Config
from streamrip.media import PendingTrack, PendingAlbum, Track
from streamrip.db import Dummy, Database
from asyncio import gather

from app.discord import send_error_msg, send_status_msg
from app.finder import get_best_match
from app.plex import refresh_library
from app.utils import get_env_var, get_search_string, print_tracks
from app.store import Store
from app.arguments import Arguments

def setup() -> tuple[YTMusic, QobuzClient, Config, Store]:
    load_dotenv()

    youtube = YTMusic('oauth.json', oauth_credentials=OAuthCredentials(client_id=get_env_var("CLIENT_ID"), client_secret=get_env_var("CLIENT_SECRET")))

    config = Config.defaults()
    config.session.qobuz.use_auth_token = True
    config.session.qobuz.email_or_userid = get_env_var("USER_ID")
    config.session.qobuz.password_or_token = get_env_var("TOKEN")
    config.session.qobuz.app_id = get_env_var("APP_ID")
    config.session.qobuz.secrets = [get_env_var("APP_SECRET")]
    config.session.downloads.folder = get_env_var("DOWNLOADS_FOLDER")
    qobuz = QobuzClient(config)

    store = Store()

    return (youtube, qobuz, config, store)

async def main(args: Arguments, ytmusic: YTMusic, qobuz: QobuzClient, qobuzConfig: Config, store: Store)->None:
    await qobuz.login()

    playlist = ytmusic.get_playlist(get_env_var("PLAYLIST_ID"), None)
    db = Database(downloads=Dummy(), failed=Dummy())

    tracks: list[Track] = []
    tracksStatus: list[tuple[Any, bool]] = []

    for item in playlist["tracks"]:
        if (store.exists(item["videoId"]) and not args.has("old")) or (args.has("old") and store.get(item["videoId"]) is not None):
            print(f"Skipping {item['title']} by {item['artists'][0]['name']} as it is in the store.")
            continue

        search_res = await qobuz.search("track", get_search_string(item))
        items = search_res[0]["tracks"]["items"]
        
        match = await get_best_match(item, items)

        store.add(item["videoId"], match[0] if match else None)

        tracksStatus.append((item, match is not None))

        if not match:
            print(f"No match found for {item['title']} by {item['artists'][0]['name']}.")
            continue

        album = await PendingAlbum(str(match[1]), qobuz, qobuzConfig, db).resolve()

        if not album:
            print(f"Album not found for {item['title']} by {item['artists'][0]['name']}.")
            continue

        track = await PendingTrack(str(match[0]), album.meta, qobuz, qobuzConfig, album.folder, db, None).resolve()

        if not track:
            print(f"Track not found for {item['title']} by {item['artists'][0]['name']}.")
            continue

        tracks.append(track)

    if args.has("list"):
        print_tracks(tracksStatus)

    if len(tracksStatus) == 0 or args.has("list"):
        return

    try:
        await gather(*[track.rip() for track in tracks])

        refresh_library()

        send_status_msg(tracksStatus)
    except Exception as e:
        print(f"An error occurred during the download process: {e}")
        send_error_msg(str(e))
        send_status_msg(tracksStatus, error=True)
        raise e
