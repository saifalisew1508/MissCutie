import requests
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CommandHandler, filters
from MissCutie import application

async def github(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("/github username")
        return

    username = context.args[0]
    URL = f"https://api.github.com/users/{username}"

    try:
        response = await requests.get(URL)
        response.raise_for_status()
        result = await response.json()

        url = result.get("html_url")
        name = result.get("name", "")
        company = result.get("company", "")
        bio = result.get("bio", "")
        created_at = result.get("created_at", "")
        avatar_url = result.get("avatar_url", "")
        blog = result.get("blog", "")
        location = result.get("location", "")
        repositories = result.get("public_repos", 0)
        followers = result.get("followers", 0)
        following = result.get("following", 0)

        caption = f"""**Info Of {name}**
**Username :** `{username}`
**Bio :** `{bio}`
**Profile link :** [{name}]({url})
**Company :** `{company}`
**Created on:** `{created_at}`
**Repositories :** `{repositories}`
**Blog :** `{blog}`
**Location :** `{location}`
**Followers  :** `{followers}`
**Following :** `{following}`"""

        await update.message.reply_photo(photo=avatar_url, caption=caption, parse_mode=ParseMode.MARKDOWN)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            await update.message.reply_text("No Github Account Found For This Username")
        else:
            print(f"Error: {e}")


application.add_handler(CommandHandler("github", github))
