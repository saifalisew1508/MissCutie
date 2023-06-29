from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot
from telegram.constants import ParseMode
from telegram.error import BadRequest, Forbidden
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

from MissCutie import application

PRIVACY_P_TEXT = """
* Our contact details * \n*Name*: @MissCutieRobot \n*Telegram*: @BotXNews
\n\nThe bot has been made to *protect* and preserve *privacy* as best as possible. \nThe proper functioning of the bot is defined as the data required for all the commands in the /help to work as expected.
\n\nOur privacy policy may change from time to time. If we make any material changes to our policies, we will place a prominent notice on https://t.me/MissCutie_Support
"""

PRIVACY_STRING = """Select one of the below options for more information about how the bot handles your privacy."""

CANCEL_STRING = """Privacy deletion request cancelled."""


async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        await update.effective_message.reply_text(
            PRIVACY_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(
                [
                  [
                    InlineKeyboardButton(text="Privacy Policy", callback_data="policy_")
                  ],
                 [
                    InlineKeyboardButton(text="Retrieve data", callback_data="policy_data"),
                    InlineKeyboardButton(text="Delete data", callback_data="policy_datadel")
                  ],
                 [
                    InlineKeyboardButton(text="Cancel", callback_data="cancel_")
                 ] 
                ]
            ),
        )

    else:
        try:
            await bot.send_message(
                user.id,
                PRIVACY_STRING,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

            await update.effective_message.reply_text(
                "This command can only used in private!"
            )
        except Forbidden:
            await update.effective_message.reply_text(
                "Contact me in pm for privacy information."
            )


  async def greyson_policy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "policy_":
        await query.message.edit_text(
            text=PRIVACY_P_TEXT,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                  [
                    InlineKeyboardButton(text="What information we collect", callback_data="policy_wiwc")
                  ],
                 [
                    InlineKeyboardButton(text="Why we collect it", callback_data="policy_wwci")
                  ],
                 [
                    InlineKeyboardButton(text="What we do", callback_data="policy_wwd")
                  ],
                 [
                    InlineKeyboardButton(text="What we DO NOT do", callback_data="policy_wwdnd")
                  ],
                 [
                    InlineKeyboardButton(text="Rights to process", callback_data="policy_rtp")
                 ] 
                ]
            ),
        )
    elif query.data == "policy_wiwc":
        await query.message.edit_text(
            text=PRIVACY_P_TEXT,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                  [
                    InlineKeyboardButton(text="• What information we collect •", callback_data="policy_wiwc")
                  ],
                 [
                    InlineKeyboardButton(text="Why we collect it", callback_data="policy_wwci")
                  ],
                 [
                    InlineKeyboardButton(text="What we do", callback_data="policy_wwd")
                  ],
                 [
                    InlineKeyboardButton(text="What we DO NOT do", callback_data="policy_wwdnd")
                  ],
                 [
                    InlineKeyboardButton(text="Rights to process", callback_data="policy_rtp")
                  ],
                 [
                    InlineKeyboardButton(text="Back", callback_data="policy_")
                 ] 
                ]
            ),
        )
    elif query.data == "policy_wwci":
        await query.message.edit_text(
            text=PRIVACY_P_TEXT,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                  [
                    InlineKeyboardButton(text="What information we collect", callback_data="policy_wiwc")
                  ],
                 [
                    InlineKeyboardButton(text="• Why we collect it •", callback_data="policy_wwci")
                  ],
                 [
                    InlineKeyboardButton(text="What we do", callback_data="policy_wwd")
                  ],
                 [
                    InlineKeyboardButton(text="What we DO NOT do", callback_data="policy_wwdnd")
                  ],
                 [
                    InlineKeyboardButton(text="Rights to process", callback_data="policy_rtp")
                  ],
                 [
                    InlineKeyboardButton(text="Back", callback_data="policy_")
                 ] 
                ]
            ),
        )
    elif query.data == "policy_wwd":
        await query.message.edit_text(
            text=PRIVACY_P_TEXT,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                  [
                    InlineKeyboardButton(text="What information we collect", callback_data="policy_wiwc")
                  ],
                 [
                    InlineKeyboardButton(text="Why we collect it", callback_data="policy_wwci")
                  ],
                 [
                    InlineKeyboardButton(text="• What we do •", callback_data="policy_wwd")
                  ],
                 [
                    InlineKeyboardButton(text="What we DO NOT do", callback_data="policy_wwdnd")
                  ],
                 [
                    InlineKeyboardButton(text="Rights to process", callback_data="policy_rtp")
                  ],
                 [
                    InlineKeyboardButton(text="Back", callback_data="policy_")
                 ] 
                ]
            ),
        )
    elif query.data == "policy_wwdnd":
        await query.message.edit_text(
            text=PRIVACY_P_TEXT,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                  [
                    InlineKeyboardButton(text="What information we collect", callback_data="policy_wiwc")
                  ],
                 [
                    InlineKeyboardButton(text="Why we collect it", callback_data="policy_wwci")
                  ],
                 [
                    InlineKeyboardButton(text="What we do", callback_data="policy_wwd")
                  ],
                 [
                    InlineKeyboardButton(text="• What we DO NOT do •", callback_data="policy_wwdnd")
                  ],
                 [
                    InlineKeyboardButton(text="Rights to process", callback_data="policy_rtp")
                  ],
                 [
                    InlineKeyboardButton(text="Back", callback_data="policy_")
                 ] 
                ]
            ),
        )
    elif query.data == "policy_rtp":
        await query.message.edit_text(
            text=f"* Rights to process *"
            f"\n\nUnder the General Data Protection Regulation (GDPR), the lawful bases we rely on for processing this information are:"
            f"\n    • Your consent. You are able to remove your consent at any time. You can do this by using the tools provided to delete your data, which will delete any data that isnt critical to bot functionality. \n    • We need it to perform a public task. Namely, allowing group or channel admins to protect their chats."
            f"\n    • We have a legitimate interest: The data collected and retained is essential to the functioning of the bot. Admins add this bot to protect their chats, and certain data is required to guarantee this."
            f"",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                  [
                    InlineKeyboardButton(text="What information we collect", callback_data="policy_wiwc")
                  ],
                 [
                    InlineKeyboardButton(text="Why we collect it", callback_data="policy_wwci")
                  ],
                 [
                    InlineKeyboardButton(text="What we do", callback_data="policy_wwd")
                  ],
                 [
                    InlineKeyboardButton(text="What we DO NOT do", callback_data="policy_wwdnd")
                  ],
                 [
                    InlineKeyboardButton(text="• Rights to process •", callback_data="policy_rtp")
                  ],
                 [
                    InlineKeyboardButton(text="Back", callback_data="policy_")
                 ] 
                ]
            ),
        )
    elif query.data == "policy_datadel":
        await query.message.edit_text(
            text="""Are you sure you want to delete your data?
Note that this will:
- delete all notes/filters you have saved to your private chat.
- delete your federation.
- remove your admin status in other federations.
- remove all your approvals from all chats.
This action **CANNOT** be undone.""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                  [
                    InlineKeyboardButton(text="Yes, delete all my data.", callback_data="policy_del")
                  ],
                 [
                    InlineKeyboardButton(text="No, I changed my mind!", callback_data="cancel_")
                  ]
                ]
            ),
        )
    elif query.data == "policy_del": 
        await query.message.edit_text(
            text="""Your data has been deleted.""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
          )
    elif query.data == "policy_data": 
        await query.message.edit_text(
            text="""These feature coming soon.""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
          )


@run_async
def greyson_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "cancel_": 
        await query.message.edit_text(
            text=""" Privacy deletion request cancelled.""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
          )

__mod_name__ = "Privacy"

__help__ = """
The privacy module allows you to see the bot privacy policy, as well as view and delete the data the bot stores about you.
*The single command which can only be used in PM:*
- /privacy: Provides all the tools relating to privacy, such as listing the privacy policy, retrieving, and deleting your data.
"""

policy_callback_handler = CallbackQueryHandler(greyson_policy_callback, pattern=r"policy_")
cancel_callback_handler = CallbackQueryHandler(greyson_cancel_callback, pattern=r"cancel_")

privacy_handler = CommandHandler("privacy", privacy)

application.add_handler(privacy_handler)
application.add_handler(cancel_callback_handler)
application.add_handler(policy_callback_handler)
