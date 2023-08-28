ADMIN_MUSIC = """Admin Commands:

Just add 'c' in the starting of the commands to use them for channel.

/pause : Pause the currently playing stream.
/resume : Resume the paused stream.
/skip : Skip the current playing stream and start streaming the next track in queue.
/end or /stop : Clears the queue and ends the current playing stream.
/player : Get an interactive player panel.
/queue : Shows the queued tracks list.
"""

AUTH_MUSIC = """
Authorized Users:

Authorized users can use admin rights in the bot without admin rights in the chat.

/auth [username/user_id] : Add a user to the auth list of the bot.
/unauth [username/user_id] : Remove a user from the auth users list.
/authusers : Show the list of auth users of the group.
"""

BROADCAST_MUSIC = """
Broadcast Feature [Only for sudoers]:

/broadcast [message or reply to a message] : Broadcast a message to served chats of the bot.

Broadcasting Modes:
-pin : Pins your broadcasted messages in served chats.
-pinloud : Pins your broadcasted messages in served chats and sends notification to the members.
-user : Broadcasts the message to the users who have started your bot.
-assistant : Broadcast your message from the assistant account of the bot.
-nobot : Forces the bot to not broadcast the message.

Example: /broadcast -user -assistant -pin Testing broadcast
"""

BLACKCHAT_MUSIC = """Chat Blacklist Feature [Only for sudoers]:

Restrict shit chats to use our precious bot.

/blacklistchat [chat_id] : Blacklist a chat from using the bot.
/whitelistchat [chat_id] : Whitelist the blacklisted chat.
/blacklistedchat : Shows the list of blacklisted chats.
"""

BLACKUSER_MUSIC = """
Block Users [Only for sudoers]:

Start ignoring the blacklisted user, so that he can't use bot commands.

/block [username or reply to a user] : Block the user from our bot.
/unblock [username or reply to a user] : Unblocks the blocked users.
/blockedusers : Shows the list of blocked users.
"""

CPLAY_MUSIC = """
Channel Play Commands:

You can stream audio/video in channel.

/cplay : Starts streaming the requested audio track on the channel's video chat.
/cvplay : Starts streaming the requested video track on the channel's video chat.
/cplayforce or /cvplayforce : Stops the ongoing stream and starts streaming the requested track.

/channelplay [chat username or id] or [disable] : Connect channel to a group and starts streaming tracks by the help of commands sent in group.
"""

GBAN_MUSIC = """
Global Ban Feature [Only for sudoers]:

/gban [username or reply to a user] : Globally bans the chutiya from all the served chats and blacklist him from using the bot.
/ungban [username or reply to a user] : Globally unbans the globally banned user.
/gbannedusers : Shows the list of globally banned users.
"""

LOOP_MUSIC = """
Loop Stream:

Starts streaming the ongoing stream in loop

/loop [enable/disable] : Enables/disables loop for the ongoing stream.
/loop [1, 2, 3, ...] : Enables loop for the given value.
"""

MAINTAINANCE_MUSIC = """
Maintenance Mode [Only for sudoers]:

/logs : Get logs of the bot.

/logger [enable/disable] : Bot will start logging the activities happened on bot.

/maintenance [enable/disable] : Enable or disable the maintenance mode of your bot.
"""

PING_MUSIC = """
Ping & Stats:

/start : Starts the music bot.
/help : Get help menu with explanation of commands.

/ping : Shows the ping and system stats of the bot.

/stats : Shows the overall stats of the bot.
"""

PLAY_MUSIC = """
Play Commands:

v stands for video play.
force stands for force play.

/play or /vplay : Starts streaming the requested track on video chat.

/playforce or /vplayforce : Stops the ongoing stream and starts streaming the requested track.
"""

SHUFFLE_MUSIC = """
Shuffle Queue:

/shuffle : Shuffles the queue.
/queue : Shows the shuffled queue.
"""

SEEK_MUSIC = """
Seek Stream:

/seek [duration in seconds] : Seeks the stream to the given duration.
/seekback [duration in seconds] : Backward seeks the stream to the given duration.
"""

SONG_MUSIC = """
Song Download:

/song [song name/yt url] : Download any track from youtube in mp3 or mp4 formats.
"""

SPEED_MUSIC = """
Speed Commands:

You can control the playback speed of the ongoing stream. [Admins only]

/speed or /playback : For adjusting the audio playback speed in group.
/cspeed or /cplayback : For adjusting the audio playback speed in channel.
"""
