from requests import get
from utils import get_env_var


def refresh_library():
    if get_env_var("ENABLE_PLEX_REFRESH").lower() != "true":
        return
    
    url = "{}://{}:{}/library/sections/{}/refresh".format(get_env_var("PLEX_SERVER_PROTOCOL"), get_env_var("PLEX_SERVER_URL"), get_env_var("PLEX_SERVER_PORT"), get_env_var("PLEX_LIBRARY_ID"))
    params = {"X-Plex-Token": get_env_var("PLEX_TOKEN")}
    response = get(url=url, params=params)
    
    if response.status_code == 200:
        print("Plex library refresh initiated successfully.")
    else:
        print(f"Failed to initiate Plex library refresh. Status code: {response.status_code}, Response: {response.text}")