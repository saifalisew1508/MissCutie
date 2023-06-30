import pyfiglet
from MissCutie.events import register


@register(pattern="^/figlet ?(.*)")
async def figlet(event):
    if event.fwd_from:
        return

    CMD_FIG = {
        "slant": "slant",
        "3D": "3-d",
        "5line": "5lineoblique",
        "alpha": "alphabet",
        "banner": "banner3-D",
        "doh": "doh",
        "iso": "isometric1",
        "letter": "letters",
        "allig": "alligator",
        "dotm": "dotmatrix",
        "bubble": "bubble",
        "bulb": "bulbhead",
        "digi": "digital",
    }

    input_str = event.pattern_match.group(1)
    if input_str is None:
        await event.edit("Please add some text to figlet")
        return

    if "|" in input_str:
        text, cmd = input_str.split("|", maxsplit=1)
        font = CMD_FIG.get(cmd)
        if font is None:
            await event.edit("Invalid selected font.")
            return
    else:
        text = input_str
        font = None

    result = pyfiglet.figlet_format(text, font=font)
    await event.respond("‌‌‎`{}`".format(result))
    await event.delete()
