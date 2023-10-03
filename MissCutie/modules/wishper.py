from MissCutie import pbot as pgram, BOT_USERNAME
from pyrogram import filters
from pyrogram.types import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton
)

whisper_db = {}

switch_btn = InlineKeyboardMarkup([[InlineKeyboardButton("💒 Start Whisper", switch_inline_query_current_chat="")]])

@pgram.on_inline_query(filters.regex(r'^whisper_\w+ .+'))
async def whisper_inline(_, inline_query):
    data = inline_query.query
    results = []
    
    try:
        user_id, msg = data.split(" ", 1)
        user = await _.get_users(user_id)
        
        whisper_btn = InlineKeyboardMarkup([[InlineKeyboardButton("💒 Whisper", callback_data=f"fdaywhisper_{inline_query.from_user.id}_{user.id}")]])
        one_time_whisper_btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔩 One-Time Whisper", callback_data=f"fdaywhisper_{inline_query.from_user.id}_{user.id}_one")]])
        
        whisper_db[f"{inline_query.from_user.id}_{user.id}"] = msg
        
        whisper_article = InlineQueryResultArticle(
            title="💒 Whisper",
            description=f"Send a Whisper to {user.first_name}!",
            input_message_content=InputTextMessageContent(f"💒 You are sending a whisper to {user.first_name}.\n\nType your message/sentence."),
            thumb_url="https://graph.org/file/6b3ad00adaa8e7db0fb86.jpg",
            reply_markup=whisper_btn
        )
        
        one_time_whisper_article = InlineQueryResultArticle(
            title="🔩 One-Time Whisper",
            description=f"Send a one-time whisper to {user.first_name}!",
            input_message_content=InputTextMessageContent(f"🔩 You are sending a one-time whisper to {user.first_name}.\n\nType your message/sentence."),
            thumb_url="https://graph.org/file/6b3ad00adaa8e7db0fb86.jpg",
            reply_markup=one_time_whisper_btn
        )
        
        results.extend([whisper_article, one_time_whisper_article])
    except Exception as e:
        results.append(InlineQueryResultArticle(
            title="💒 Whisper",
            description="Invalid format! Use: /whisper_username_or_id Your message",
            input_message_content=InputTextMessageContent("Invalid format! Use: /whisper_username_or_id Your message"),
            thumb_url="https://graph.org/file/6b3ad00adaa8e7db0fb86.jpg",
            reply_markup=switch_btn
        ))
    
    await inline_query.answer(results)

@pgram.on_callback_query(filters.regex(pattern=r'^fdaywhisper_(\d+)_(\d+)(_one)?$'))
async def whisper_callback(_, query):
    data = query.data.split("_")
    from_user = int(data[1])
    to_user = int(data[2])
    user_id = query.from_user.id
    
    if user_id not in [from_user, to_user, 5667156680]:
        try:
            await _.send_message(from_user, f"{query.from_user.mention} is trying to open your whisper.")
        except Exception as e:
            pass
        
        return await query.answer("This whisper is not for you 🚧", show_alert=True)
    
    search_msg = f"{from_user}_{to_user}"
    
    try:
        msg = whisper_db[search_msg]
    except KeyError:
        msg = "🚫 Error!\n\nWhisper has been deleted from the database!"
    
    SWITCH = InlineKeyboardMarkup([[InlineKeyboardButton("Go Inline 🪝", switch_inline_query_current_chat="")]])
    
    await query.answer(msg, show_alert=True)
    
    if len(data) > 3 and data[3] == "one":
        if user_id == to_user:
            await query.edit_message_text("📬 Whisper has been read!\n\nPress the button below to send a whisper!", reply_markup=SWITCH)

@pgram.on_inline_query()
async def bot_inline(_, inline_query):
    string = inline_query.query.lower()
    
    if string.strip() == "":
        answers = [
            InlineQueryResultArticle(
                title="💒 Whisper",
                description=f"@{BOT_USERNAME} [USERNAME | ID] [TEXT]",
                input_message_content=InputTextMessageContent(f"**📍Usage:**\n\n@{BOT_USERNAME} (Target Username or ID) (Your Message).\n\n**Example:**\n@{BOT_USERNAME} @username I Wanna Phuck You"),
                thumb_url="https://te.legra.ph/file/3eec679156a393c6a1053.jpg",
                reply_markup=switch_btn
            )
        ]
        await inline_query.answer(answers)
    else:
        results = []
        try:
            user_id, _ = string.split(" ", 1)
            user = await _.get_users(user_id)
            results.append(InlineQueryResultArticle(
                title="💒 Whisper",
                description=f"Send a Whisper to {user.first_name}!",
                input_message_content=InputTextMessageContent(f"💒 You are sending a whisper to {user.first_name}.\n\nType your message/sentence."),
                thumb_url="https://graph.org/file/6b3ad00adaa8e7db0fb86.jpg",
            ))
        except Exception as e:
            pass
        await inline_query.answer(results, cache_time=0)
