from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import BadRequest
from telegram.ext import CommandHandler, run_async, Filters
from telegram.utils.helpers import escape_markdown

import tg_bot.modules.sql.rules_sql as sql
from tg_bot import dispatcher
from tg_bot.modules.helper_funcs import user_admin, markdown_parser


@run_async
def get_rules(bot, update):
    chat_id = update.effective_chat.id
    send_rules(update, chat_id)


def send_rules(update, chat_id, from_pm=False):
    bot = dispatcher.bot
    user = update.effective_user
    try:
        chat = bot.get_chat(chat_id)
    except BadRequest as excp:
        if excp.message == "Chat not found" and from_pm:
            bot.send_message(user.id, "The rules shortcut hasn't been set properly for this chat! Ask admins to "
                                      "fix this.")
            return
        else:
            raise

    rules = sql.get_rules(chat_id)
    text = "The rules for *{}* are:\n\n{}".format(escape_markdown(chat.title), rules)

    if from_pm and rules:
        bot.send_message(user.id, text, parse_mode=ParseMode.MARKDOWN)
    elif from_pm:
        bot.send_message(user.id, "The group admins haven't set any rules for this chat yet. "
                                  "This probably doesn't mean it's lawless though...!")
    elif rules:
        update.effective_message.reply_text("Contact me in PM to get this group's rules.",
                                            reply_markup=InlineKeyboardMarkup(
                                                [[InlineKeyboardButton(text="Rules",
                                                                       url="t.me/{}?start={}".format(bot.username,
                                                                                                     chat_id))]]))
    else:
        update.effective_message.reply_text("The group admins haven't set any rules for this chat yet. "
                                            "This probably doesn't mean it's lawless though...!")


@run_async
@user_admin
def set_rules(bot, update):
    chat_id = update.effective_chat.id
    msg = update.effective_message
    raw_text = msg.text
    args = raw_text.split(None, 1)  # use python's maxsplit to separate cmd and args
    if len(args) == 2:
        txt = args[1]
        offset = len(txt) - len(raw_text)  # set correct offset relative to command
        markdown_rules = markdown_parser(txt, entities=msg.parse_entities(), offset=offset)

        sql.set_rules(chat_id, markdown_rules)
        update.effective_message.reply_text("done, You can Rule Now")


@run_async
@user_admin
def clear_rules(bot, update):
    chat_id = update.effective_chat.id
    sql.set_rules(chat_id, "")
    update.effective_message.reply_text("Successfully cleared rules!")


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


__help__ = """
 - /rules: get the rules for this chat.
 - /setrules <your rules here>: set the rules for this chat.
 - /clearrules: clear the rules for this chat.
"""

__name__ = "Rules"

GET_RULES_HANDLER = CommandHandler("rules", get_rules, filters=Filters.group)
SET_RULES_HANDLER = CommandHandler("setrules", set_rules, filters=Filters.group)
RESET_RULES_HANDLER = CommandHandler("clearrules", clear_rules, filters=Filters.group)

dispatcher.add_handler(GET_RULES_HANDLER)
dispatcher.add_handler(SET_RULES_HANDLER)
dispatcher.add_handler(RESET_RULES_HANDLER)
