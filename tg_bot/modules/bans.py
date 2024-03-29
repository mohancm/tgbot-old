from telegram.error import BadRequest
from telegram.ext import run_async, CommandHandler, Filters

from tg_bot import dispatcher, BAN_STICKER
from tg_bot.modules.helper_funcs import bot_admin, user_admin, is_user_admin, is_user_in_chat, extract_user, \
    can_restrict, is_user_ban_protected


@run_async
@bot_admin
@user_admin
def ban(bot, update, args):
    chat = update.effective_chat
    message = update.effective_message

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text("You don't seem to be referring to a user.")
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user")
            return
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I really wish I could ban admins...")
        return

    if user_id == bot.id:
        update.effective_message.reply_text("I'm not gonna BAN myself, are you crazy?")
        return

    res = update.effective_chat.kick_member(user_id)
    if res:
        bot.send_sticker(update.effective_chat.id, BAN_STICKER)  # banhammer marie sticker
        message.reply_text("*takes out Mjölnir* Banned!")
    else:
        message.reply_text("Well damn, I can't ban that user.")


@run_async
@bot_admin
@can_restrict
@user_admin
def kick(bot, update, args):
    chat = update.effective_chat
    message = update.effective_message

    user_id = extract_user(message, args)
    if not user_id:
        return

    if is_user_ban_protected(chat, user_id):
        message.reply_text("I really wish I could kick admins...")
        return

    if user_id == bot.id:
        update.effective_message.reply_text("Yeahhh I'm not gonna do that")
        return

    res = update.effective_chat.unban_member(user_id)  # unban on current user = kick
    if res:
        bot.send_sticker(update.effective_chat.id, BAN_STICKER)  # banhammer marie sticker
        message.reply_text("Kicked!")
    else:
        message.reply_text("Well damn, I can't kick that user.")


@run_async
@bot_admin
@can_restrict
def kickme(bot, update):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("I wish I could... but you're an admin.")
        return

    res = update.effective_chat.unban_member(user_id)  # unban on current user = kick
    if res:
        update.effective_message.reply_text("No problem.")
    else:
        update.effective_message.reply_text("Huh? I can't :/")


@run_async
@bot_admin
@user_admin
def unban(bot, update, args):
    message = update.effective_message
    chat = update.effective_chat

    user_id = extract_user(message, args)
    if not user_id:
        return

    if user_id == bot.id:
        update.effective_message.reply_text("How would I unban myself if I wasn't here...?")
        return

    if is_user_in_chat(chat, user_id):
        update.effective_message.reply_text("Why are you trying to unban someone that's already in the chat?")
        return

    res = update.effective_chat.unban_member(user_id)
    if res:
        message.reply_text("Yeah, he can join back now.!")
    else:
        message.reply_text("Hm, couldn't unban this person.")


__help__ = """
 - /ban <userhandle>: bans a user. (via handle, or reply)
 - /unban <userhandle>: unbans a user. (via handle, or reply)
 - /kick <userhandle>: kicks a user, (via handle, or reply)
 - /kickme: kicks the user who issued the command
 """

__name__ = "Bans"


BAN_HANDLER = CommandHandler("ban", ban, pass_args=True, filters=~Filters.private)
KICK_HANDLER = CommandHandler("kick", kick, pass_args=True, filters=~Filters.private)
UNBAN_HANDLER = CommandHandler("unban", unban, pass_args=True, filters=~Filters.private)
KICKME_HANDLER = CommandHandler("kickme", kickme, filters=~Filters.private)

dispatcher.add_handler(BAN_HANDLER)
dispatcher.add_handler(KICK_HANDLER)
dispatcher.add_handler(UNBAN_HANDLER)
dispatcher.add_handler(KICKME_HANDLER)
