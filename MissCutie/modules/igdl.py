from pyrogram import filters
import instaloader
import requests
import os
from MissCutie import pbot as app
from MissCutie import pbot as client




@app.on_message(filters.command("ig", prefixes="/"))
def save_instagram_post(client, message):
    url = message.text.split(" ")[1]
    try:
        if "/p/" in url:
            # If it's a post
            post_code = url.split("/p/")[1].split("/")[0]
            downloader = instaloader.Instaloader()
            downloader.download_post(post_code, target="saved_posts")
            media_path = f"saved_posts/{post_code}.jpg"
            caption = "Instagram Post:"
        elif "/reel/" in url:
            # If it's a reel
            reel_code = url.split("/reel/")[1].split("/")[0]
            downloader = instaloader.Instaloader()
            downloader.download_reels(reel_code, target="saved_reels")
            media_path = f"saved_reels/{reel_code}.mp4"
            caption = "Instagram Reel:"
        elif "/tv/" in url:
            # If it's an IGTV video
            igtv_code = url.split("/tv/")[1].split("/")[0]
            downloader = instaloader.Instaloader()
            downloader.download_igtv(igtv_code, target="saved_igtv")
            media_path = f"saved_igtv/{igtv_code}.mp4"
            caption = "Instagram IGTV:"
        elif "/stories/" in url:
            # If it's a story
            story_username = url.split("/stories/")[1].split("/")[0]
            story_id = url.split("/stories/")[1].split("/")[1]
            response = requests.get(f"https://www.instagram.com/{story_username}/stories/archive/reel/{story_id}/")
            json_data = response.json()
            story_url = json_data["data"]["reels_media"][0]["display_url"]
            r = requests.get(story_url)
            media_path = f"saved_stories/story_{story_id}.jpg"
            with open(media_path, "wb") as f:
                f.write(r.content)
            caption = "Instagram Story:"
        else:
            client.send_message(message.chat.id, "Invalid URL! Please provide a valid Instagram post, reel, IGTV, or story URL.")
            return

        # Send the media as a Telegram message
        client.send_chat_action(message.chat.id, "upload_photo" if media_path.endswith(".jpg") else "upload_video")
        client.send_document(
            chat_id=message.chat.id,
            document=media_path,
            caption=caption
        )
        os.remove(media_path)  # Remove the downloaded media file

    except Exception as e:
        client.send_message(message.chat.id, f"An error occurred while processing the content: {str(e)}")
