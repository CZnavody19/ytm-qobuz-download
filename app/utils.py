from os import getenv
from typing import Any

def get_env_var(name:str) -> str:
    val = getenv(name)
    if not val:
        raise ValueError(f"Environment variable '{name}' is not set.")
    return val

def get_search_string(item) -> str:
    return "{} {}".format(item["title"], item["artists"][0]["name"])

def print_tracks(tracks: list[tuple[Any, bool]]) -> None:
    for item, status in tracks:
        print(f"{item['title']} by {item['artists'][0]['name']}: {'Found' if status else 'Not Found'}")
    print(f"Total tracks processed: {len(tracks)}")
    print(f"Tracks found: {sum(1 for _, status in tracks if status)}")
    print(f"Tracks not found: {sum(1 for _, status in tracks if not status)}")