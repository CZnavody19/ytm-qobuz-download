from asyncio import run
from app.discord import send_error_msg
from app.main import main, setup
from app.arguments import Arguments
from sys import argv

from app.plex import refresh_library

args = Arguments([
    ("l", "list", "List all tracks with their status"),
    ("r", "refresh", "Only refresh the Plex library"),
    ("o", "old", "Try to redownload old not found tracks"),
])

async def run_main():
    if not args.parse(argv[1:]):
        return

    if args.has("refresh"):
        return refresh_library()

    ytmusic, qobuz, qobuzConfig, store = setup()

    try:
        await main(args, ytmusic, qobuz, qobuzConfig, store)
        store.save()
    except Exception as e:
        print(f"An error occurred: {e}")
        send_error_msg(str(e))
    finally:
        await qobuz.session.close()

if __name__ == "__main__":
    run(run_main())
