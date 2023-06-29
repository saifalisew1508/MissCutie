"""
import asyncio
import instaloader
import requests
from pyrogram import filters
import os
from MissCutie import pbot as app
from MissCutie import pbot as client



L = instaloader.Instaloader()
L.login("im_broken2023", "Saif@1508")



async def download_instagram_post(post_code, target_folder):
    post = instaloader.Post.from_shortcode(L.context, post_code)
    await L.download_post(post, target=target_folder)

async def download_instagram_story(username, target_folder):
    profile = instaloader.Profile.from_username(L.context, username)
    stories = profile.get_stories()
    for story in stories:
        await L.download_storyitem(story, target=target_folder)

async def download_instagram_igtv(igtv_code, target_folder):
    igtv = instaloader.IGTV.from_shortcode(L.context, igtv_code)
    await L.download_igtv([igtv], target=target_folder)

async def download_instagram_reel(reel_code, target_folder):
    reel = instaloader.Post.from_shortcode(L.context, reel_code)
    await L.download_reels([reel], target=target_folder)

@app.on_message(filters.command("ig", prefixes="/"))
async def save_instagram_content(client, message):
    url = message.text.split(" ")[1]
    try:
        if "/p/" in url:
            # If it's a post
            post_code = url.split("/p/")[1].split("/")[0]
            media_path = f"saved_posts/{post_code}.jpg"
            await download_instagram_post(post_code, "saved_posts")
            caption = "Instagram Post:"
            is_photo = True
        elif "/stories/" in url:
            # If it's a story
            username = url.split("/stories/")[1].split("/")[0]
            media_path = f"saved_stories/{username}"
            await download_instagram_story(username, "saved_stories")
            caption = "Instagram Story:"
            is_photo = True
        elif "/reel/" in url:
            # If it's a reel
            reel_code = url.split("/reel/")[1].split("/")[0]
            media_path = f"saved_reels/{reel_code}.mp4"
            await download_instagram_reel(reel_code, "saved_reels")
            caption = "Instagram Reel:"
            is_photo = False
        elif "/tv/" in url:
            # If it's an IGTV video
            igtv_code = url.split("/tv/")[1].split("/")[0]
            media_path = f"saved_igtv/{igtv_code}.mp4"
            await download_instagram_igtv(igtv_code, "saved_igtv")
            caption = "Instagram IGTV:"
            is_photo = False
        else:
            await client.send_message(message.chat.id, "Invalid URL! Please provide a valid Instagram post, reel, IGTV, or story URL.")
            return

        # Send the media as a Telegram message
        await client.send_chat_action(message.chat.id, "upload_photo" if is_photo else "upload_video")
        if is_photo:
            await client.send_photo(
                chat_id=message.chat.id,
                photo=media_path,
                caption=caption
            )
        else:
            await client.send_video(
                chat_id=message.chat.id,
                video=media_path,
                caption=caption
            )
        os.remove(media_path)  # Remove the downloaded media file

    except Exception as e:
        await client.send_message(message.chat.id, f"An error occurred while processing the content: {str(e)}")
