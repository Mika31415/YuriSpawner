# ----- Modules -----
import asyncio
import threading
import time

# ----- Custom Modules -----
import Helper.yuri as yuri
import Helper.obs as obs
import Helper.twitch as twitch

# ----- Global Variables -----
GET_POSTS_INTERVAL = 600 # Get new Posts every 10 Min
CLEANUP_INTERAL = 2 # Check every 2 Sec if Images are too old
IMAGES_PER_REDEEM = 10 # Spawn X Images on every Redeem (Follow rn)

posts = []
obs_client = None

# ----- In Background: Get new posts -----
def refresh_posts_loop():
    global posts
    while True:
        posts = yuri.search_images()
        time.sleep(GET_POSTS_INTERVAL)

# ----- In Background: Clean up old posts -----
def cleanup_loop():
    while True:
        obs.cleanup_old_sources(obs_client)
        time.sleep(CLEANUP_INTERAL)

# ----- Check If Event happens -----
async def on_redemption(data):
    print(f"{data.event.user_name} redeemed Yuri!!!")
    for _ in range(IMAGES_PER_REDEEM):
        path = yuri.get_random_yuri_image(posts)
        if path:
            obs.spawn_yuri_image(obs_client, path)

# ----- The COMPLETE Main Loop -----
async def main():
    global obs_client, posts

    obs_client = obs.connect_to_obs()
    posts = yuri.search_images()

    threading.Thread(target=refresh_posts_loop, daemon=True).start()
    threading.Thread(target=cleanup_loop, daemon=True).start()

    tw = await twitch.authenticate()
    broadcaster_id = await twitch.get_broadcaster_id(tw, twitch.USERNAME)
    eventsub = await twitch.start_eventsub(tw, broadcaster_id, on_redemption)

    try:
        input("Press enter to stop...\n")
    except KeyboardInterrupt:
        pass
    finally:
        await eventsub.stop()
        await tw.close()

# ----- Testing / Running -----
if __name__ == '__main__':
    asyncio.run(main())