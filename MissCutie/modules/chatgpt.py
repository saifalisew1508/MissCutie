import openai
import asyncio
import html
from aiohttp import ClientSession
from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.errors import MessageTooLong

from MissCutie import pbot as app

from MissCutie.utils.media_helper import post_to_telegraph 
from MissCutie.utils.time_gap import check_time_gap
from MissCutie.utils.post import http
from MissCutie.utils.ratelimiter import ratelimiter
from MissCutie import DEV_USERS as SUDO

openai.api_key = "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"

# This only for testing things, since maybe in future it will got blocked
@app.on_message(filters.command("bard"))
async def bard_chatbot(self: Client, ctx: Message):
    if len(ctx.command) == 1:
        return await ctx.reply_msg("Please use command <code>/{cmd} [question]</code> to ask your question.format(cmd=ctx.command[0])", quote=True, del_in=5)
    msg = await ctx.reply_msg("Wait a moment looking for your answer.", quote=True)
    data = {'message': ctx.input, 'session_id':'XQjzKRYITZ7fhplF-rXa_GTynUwdctKq4aGm-lqUCCJzF98xqDulL9UKopIadNpQn0lvnA.'}
    try:
        req = await http.post("https://bard-api-rho.vercel.app/ask", json=data)
        await msg.edit_msg(req.json().get("content"))
    except Exception as e:
        await msg.edit_msg(str(e))

@app.on_message(filters.command("ask"))
@ratelimiter
async def openai_chatbot(self: Client, ctx: Message):
    if len(ctx.command) == 1:
        return await ctx.reply_msg(Please use command <code>/{cmd} [question]</code> to ask your question.format(cmd=ctx.command[0]), quote=True, del_in=5)
    uid = ctx.from_user.id if ctx.from_user else ctx.sender_chat.id
    is_in_gap, sleep_time = await check_time_gap(uid)
    if is_in_gap and (uid not in SUDO):
        return await ctx.reply_msg("Don't spam please, please wait {tm} second or i will ban you from this bot", del_in=5)
    openai.aiosession.set(ClientSession())
    pertanyaan = ctx.input
    msg = await ctx.reply_msg("Wait a moment looking for your answer..", quote=True)
    num = 0
    answer = ""
    try:
        response = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo", messages=[{"role": "user", "content": pertanyaan}], temperature=0.7, stream=True)
        async for chunk in response:
            if not chunk.choices[0].delta or chunk.choices[0].delta.get("role"):
                continue
            num += 1
            answer += chunk.choices[0].delta.content
            if num == 30:
                await msg.edit_msg(answer)
                await asyncio.sleep(1.5)
                num = 0
        await msg.edit_msg(answer)
    except MessageTooLong:
        answerlink = await post_to_telegraph(False, "MissCutie ChatBot ", html.escape(answer))
        await msg.edit_msg("Question for your answer has exceeded TG text limit, check this link to view.\n\n{answerlink}".format(answerlink=answerlink), disable_web_page_preview=True)
    except Exception as err:
        await msg.edit_msg(f"ERROR: {str(err)}")
    await openai.aiosession.get().close()
