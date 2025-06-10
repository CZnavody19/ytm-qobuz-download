from typing import Any
from requests import post
from utils import get_env_var


def send_message(body: dict[str, Any]) -> None:
    if get_env_var("ENABLE_DISCORD_NOTIFICATIONS").lower() != "true":
        return
    
    response = post(url=get_env_var("DISCORD_WEBHOOK_URL"), json=body)

    if response.ok:
        print("Discord notification sent successfully.")
    else:
        print(f"Failed to send Discord notification. Status code: {response.status_code}, Response: {response.text}")

def send_status_msg(tracks: list[tuple[Any, bool]], error: bool = False):
    vals = {
        True: "Downloaded",
        False: "Not downloaded"
    } if not error else {
        True: "Would download",
        False: "Would not download"
    }

    body = {
        "embeds": [
            {
                "title": "Download status",
                "fields": [
                    {
                        "name": "{} by {}".format(track[0]["title"], track[0]["artists"][0]["name"]),
                        "value": vals[track[1]],
                        "inline": False
                    } for track in tracks
                ]
            }
        ]
    }
     
    send_message(body)

def send_error_msg(error: str):
    body = {
        "embeds": [
            {
                "title": "Error occurred",
                "description": error,
                "color": 16711680  # Red color
            }
        ]
    }
    
    send_message(body)