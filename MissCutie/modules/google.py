import os
import re
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup
from PIL import Image
import requests

from MissCutie import telethn as tbot
from MissCutie.events import register


opener = urllib.request.build_opener()
user_agent = "Mozilla/5.0 (Linux; Android 11; SM-M017F Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.157 Mobile Safari/537.36"
opener.addheaders = [("User-agent", user_agent)]


@register(pattern=r"^/google (.*)")
async def google_search(event):
    if event.fwd_from:
        return

    query = event.pattern_match.group(1)
    page = re.findall(r"page=(\d+)", query)
    page = int(page[0]) if page else 1
    query = re.sub(r"page=\d+", "", query).strip()

    webevent = await event.reply("Searching...")
    search_args = (query, page)
    gsearch = GoogleSearch()
    gresults = await gsearch.async_search(*search_args)
    msg = ""
    for i in range(len(gresults["links"])):
        try:
            title = gresults["titles"][i]
            link = gresults["links"][i]
            desc = gresults["descriptions"][i]
            msg += f"➥[{title}]({link})\n**{desc}**\n\n"
        except IndexError:
            break
    await webevent.edit(
        "**Search Query:**\n`" + query + "`\n\n**Results:**\n" + msg, link_preview=False
    )


@register(pattern=r"^/img (.*)")
async def image_search(event):
    if event.fwd_from:
        return

    query = event.pattern_match.group(1)
    jit = f'"{query}"'
    downloader.download(
        jit,
        limit=4,
        output_dir="store",
        adult_filter_off=False,
        force_replace=False,
        timeout=60,
    )
    os.chdir(f"./store/{query}")
    types = ("*.png", "*.jpeg", "*.jpg")
    files_grabbed = []
    for file_type in types:
        files_grabbed.extend(glob.glob(file_type))
    await tbot.send_file(event.chat_id, files_grabbed, reply_to=event.id)
    os.chdir("/app")
    os.system("rm -rf store")


@register(pattern=r"^/(reverse|pp|grs)(?: |$)(\d*)")
async def reverse_image_search(event):
    if os.path.isfile("okgoogle.png"):
        os.remove("okgoogle.png")

    message = await event.get_reply_message()
    if not message or not message.media:
        await event.reply("`Reply to a photo or sticker.`")
        return

    dev = await event.reply("`Processing...`")
    photo = await tbot.download_media(message)
    try:
        image = Image.open(photo)
    except OSError:
        await dev.edit("`Unsupported image format.`")
        return

    name = "okgoogle.png"
    image.save(name, "PNG")
    image.close()
    
    search_url = "https://www.google.com/searchbyimage/upload"
    multipart = {"encoded_image": (name, open(name, "rb")), "image_content": ""}
    response = requests.post(search_url, files=multipart, allow_redirects=False)
    fetch_url = response.headers.get("Location")

    if response.status_code == 400:
        await dev.edit("`Error: Could not find image.`")
        return

    os.remove(name)

    match = False
    if event.pattern_match.group(1) == "reverse":
        match = True
        text = "`Image successfully uploaded. Looking for matches...`"
    elif event.pattern_match.group(1) == "pp":
        text = "`Performing a reverse image search...`"
    elif event.pattern_match.group(1) == "grs":
        text = "`Performing a Google reverse search...`"
    await dev.edit(text)

    if len(event.pattern_match.group(2)) != 0:
        limit = int(event.pattern_match.group(2))
    else:
        limit = 10

    await _reverse_search_logic(event, fetch_url, limit, match)


@register(pattern=r"^/app (.*)")
async def app_search(event):
    if event.fwd_from:
        return

    query = event.pattern_match.group(1)
    result = ""

    res = requests.get(
        f"https://play.google.com/store/search?q={query}&c=apps&hl=en"
    )
    soup = BeautifulSoup(res.text, "html.parser")

    for i in soup.findAll("a", href=True, attrs={"class": "poRVub"}):
        title = i.find("div", attrs={"class": "WsMG1c nnK0zc"}).text
        link = "https://play.google.com" + i["href"]
        desc = i.find("div", attrs={"class": "KoLSrc"}).text
        developer = i.find("span", attrs={"class": "KoLSrc"}).text
        icon = i.find("img", attrs={"class": "T75of TJ3h3c"})
        try:
            await event.reply(file=icon["src"], caption=f"{title}\n{desc}\n{developer}\n{link}")
        except TypeError:
            await event.reply(f"{title}\n{desc}\n{developer}\n{link}")

    await event.reply(result)


async def _reverse_search_logic(event, fetch_url, limit, match):
    response = requests.get(fetch_url)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    try:
        for div in soup.findAll("div", attrs={"class": "r5a77d"}):
            try:
                results.append(div.a["href"])
            except KeyError:
                pass
    except Exception as e:
        await event.reply("`Error: Cannot connect to Google.`")
        return

    if match:
        if len(results) == 0:
            await event.reply("`No visually similar images found.`")
            return
        result = results[0]
        await event.reply(
            "**Image match found!**\n\n" f"➥ [Click Here]({result})", link_preview=False
        )
    else:
        count = 0
        text = "**Google Reverse Search:**\n"
        for result in results:
            if count == limit:
                break
            count += 1
            text += f"\n[Link {count}]({result})"

        if count == 0:
            text = "`No results found.`"

        await event.reply(text, link_preview=False)


class GoogleSearch:
    async def async_search(self, query, page=1):
        search_url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query) + "&start=" + str(
            (page - 1) * 10)
        response = opener.open(search_url)
        soup = BeautifulSoup(response, "html.parser")
        results = []
        titles = []
        descriptions = []
        links = []
        try:
            for g in soup.find_all(class_="g"):
                rc = g.find(class_="r")
                if rc:
                    href = rc.a["href"]
                    link = re.findall(r"(?<=url\?q=).*?(?=&sa=)", href)[0]
                    title = rc.get_text()
                    description = g.find(class_="st").get_text()
                    results.append((title, link, description))
                    titles.append(title)
                    links.append(link)
                    descriptions.append(description)
        except Exception as e:
            print(str(e))
        return {
            "results": results,
            "titles": titles,
            "links": links,
            "descriptions": descriptions,
        }



__mod_name__ = "Google"

__help__ = """
 ➥ /google <text>*:* Perform a google search
 ➥ /img <text>*:* Search Google for images and returns them\nFor greater no. of results specify lim, For eg: `/img hello lim=10`
 ➥ /app <appname>*:* Searches for an app in Play Store and returns its details.
 ➥ /reverse |pp |grs: Does a reverse image search of the media which it was replied to.

"""
