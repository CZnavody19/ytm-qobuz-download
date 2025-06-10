from typing import Any
from ytmusicapi import YTMusic, OAuthCredentials
from dotenv import load_dotenv
from streamrip.client import QobuzClient, DeezerClient
from streamrip.config import Config
from streamrip.media import PendingTrack, PendingAlbum, Track
from streamrip.db import Dummy, Database
from asyncio import run, gather
from requests import get, post

from finder import get_best_match
from utils import get_env_var, get_search_string
from store import Store

def setup() -> tuple[YTMusic, QobuzClient, DeezerClient, Config, Store]:
    load_dotenv()

    youtube = YTMusic('oauth.json', oauth_credentials=OAuthCredentials(client_id=get_env_var("CLIENT_ID"), client_secret=get_env_var("CLIENT_SECRET")))

    config = Config.defaults()
    config.session.downloads.folder = get_env_var("DOWNLOADS_FOLDER")

    config.session.qobuz.use_auth_token = True
    config.session.qobuz.email_or_userid = get_env_var("USER_ID")
    config.session.qobuz.password_or_token = get_env_var("TOKEN")
    config.session.qobuz.app_id = get_env_var("APP_ID")
    config.session.qobuz.secrets = [get_env_var("APP_SECRET")]

    # config.session.deezer.arl = get_env_var("DEEZER_ARL")

    qobuz = QobuzClient(config)
    deezer = DeezerClient(config)

    store = Store()

    return (youtube, qobuz, deezer, config, store)

async def main(ytmusic: YTMusic, qobuz: QobuzClient, deezer: DeezerClient, config: Config, store: Store)->None:
    await gather(
        qobuz.login(),
        # deezer.login(),
    )

    db = Database(downloads=Dummy(), failed=Dummy())

    playlist = ytmusic.get_playlist(get_env_var("PLAYLIST_ID"), None)

    tracks: list[Track] = []
    tracksStatus: list[tuple[Any, bool]] = []

    for item in playlist["tracks"]:
        if store.exists(item["videoId"]):
            print(f"Skipping {item['title']} by {item['artists'][0]['name']} as it is in the store.")
            continue

        [qobuz_search_res, deezer_search_res] = await gather(
            qobuz.search("track", get_search_string(item)),
            deezer.search("track", get_search_string(item))
        )

        print(deezer_search_res)

        match = await get_best_match(item, qobuz_search_res[0]["tracks"]["items"])

        store.add(item["videoId"], match[0] if match else None)

        tracksStatus.append((item, match is not None))

        if not match:
            print(f"No match found for {item['title']} by {item['artists'][0]['name']}.")
            continue

        album = await PendingAlbum(str(match[1]), qobuz, config, db).resolve()

        if not album:
            print(f"Album not found for {item['title']} by {item['artists'][0]['name']}.")
            continue

        track = await PendingTrack(str(match[0]), album.meta, qobuz, config, album.folder, db, None).resolve()

        if not track:
            print(f"Track not found for {item['title']} by {item['artists'][0]['name']}.")
            continue

        tracks.append(track)

    await gather(*[track.rip() for track in tracks])

    if get_env_var("ENABLE_PLEX_REFRESH").lower() == "true":
        url = "{}://{}:{}/library/sections/{}/refresh".format(get_env_var("PLEX_SERVER_PROTOCOL"), get_env_var("PLEX_SERVER_URL"), get_env_var("PLEX_SERVER_PORT"), get_env_var("PLEX_LIBRARY_ID"))
        params = {"X-Plex-Token": get_env_var("PLEX_TOKEN")}
        response = get(url=url, params=params)
        
        if response.status_code == 200:
            print("Plex library refresh initiated successfully.")
        else:
            print(f"Failed to initiate Plex library refresh. Status code: {response.status_code}, Response: {response.text}")

    if get_env_var("ENABLE_DISCORD_NOTIFICATIONS").lower() == "true" and len(tracksStatus) > 0:
        body = {
            "embeds": [
                {
                    "title": "Download status",
                    "fields": [
                        {
                            "name": "{} by {}".format(track[0]["title"], track[0]["artists"][0]["name"]),
                            "value": "Downloaded" if track[1] else "Not downloaded",
                            "inline": False
                        } for track in tracksStatus
                    ]
                }
            ]
        }
        response = post(url=get_env_var("DISCORD_WEBHOOK_URL"), json=body)

        if response.ok:
            print("Discord notification sent successfully.")
        else:
            print(f"Failed to send Discord notification. Status code: {response.status_code}, Response: {response.text}")

async def run_main():
    ytmusic, qobuz, deezer, qobuzConfig, store = setup()

    try:
        await main(ytmusic, qobuz, deezer, qobuzConfig, store)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        store.save()
        await qobuz.session.close()
        await deezer.session.close()

if __name__ == "__main__":
    run(run_main())
