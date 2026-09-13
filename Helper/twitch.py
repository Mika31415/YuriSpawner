# ----- Modules -----
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.object.eventsub import ChannelFollowEvent
from twitchAPI.helper import first
import os

# -----------------------------------------------------------------------
# ------------- Global Variables: Change it to your liking --------------
# -----------------------------------------------------------------------
APP_ID = os.getenv("TWITCH_CLIENT_ID") # Your App ID
APP_SECRET = os.getenv("TWITCH_CLIENT_SECRET") # Your Hidden App Token
TARGET_SCOPES = [AuthScope.MODERATOR_READ_FOLLOWERS] # Your Twitch Events
USERNAME = "mika31415" # Your Twitch Username

USE_MOCK = False  # If True, Mock Test Server | If False, real Twitch
# -----------------------------------------------------------------------

# ----- Login for the Twitch API ----- 
async def authenticate():
    twitch = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(twitch, TARGET_SCOPES, url="http://localhost:17563")
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, TARGET_SCOPES, refresh_token)
    return twitch

# ----- Get the user ID of the streamer for later -----
async def get_broadcaster_id(twitch, username):
    user = await first(twitch.get_users(logins=[username]))
    return user.id

# ----- Get a Print Message on follow -----
async def on_follow(data: ChannelFollowEvent):
    print(f"{data.event.user_name} follows {data.event.broadcaster_user_name} now!")

# ----- Start the event loop -----
async def start_eventsub(twitch, broadcaster_id, callback):
    if USE_MOCK:
        eventsub = EventSubWebsocket(
            twitch,
            connection_url="ws://127.0.0.1:8080/ws",
            subscription_url="http://127.0.0.1:8080/"
        )
    else:
        eventsub = EventSubWebsocket(twitch)

    eventsub.start()
    sub_id = await eventsub.listen_channel_follow_v2(broadcaster_id, broadcaster_id, callback)

    if USE_MOCK:
        print(f"twitch event trigger channel.follow -t {broadcaster_id} -u {sub_id} -T websocket")

    return eventsub

# ----- Combine everything in 1 single Function -----
async def main():
    twitch = await authenticate()
    broadcaster_id = await get_broadcaster_id(twitch, USERNAME, on_follow)
    eventsub = await start_eventsub(twitch, broadcaster_id)
    
    try:
        input("Press enter to stop...\n")
    except KeyboardInterrupt:
        pass
    finally:
        await eventsub.stop()
        await twitch.close()

# ----- Testing -----
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())