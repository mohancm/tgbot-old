import json
import random
from datetime import datetime

import requests
from telegram import ParseMode
from telegram.ext import CommandHandler, run_async, Filters
from telegram.utils.helpers import escape_markdown

from tg_bot import dispatcher, OWNER_ID, SUDO_USERS, SUPPORT_USERS, WHITELIST_USERS, BAN_STICKER
from tg_bot.__main__ import STATS, USER_INFO
from tg_bot.modules.helper_funcs import CustomFilters, extract_user

RUN_STRINGS = (
    "Where da heck you think ya going?",
    "Trying to get away?",
    "Run baby run imma coming...",
    "Come on, come back ",
    "You ain't so fast kid",
    "Bangs a wall!",
    "Don't leave me alone!!",
    "You run alone, you die alone.",
    "Can't stop running eh?",
    "You're gonna regret this..",
    "Why run when you can /kickme",
    "No-one here cares.",
    "You know nothing..nothin....",
    "Run for ya life, tho it is of no value?",
    "Walkers are coming, run for ya life..",
    "Is Darth Vader around?.",
    "May the odds be ever in your favour.",
    "Famous last wordswords before fapping",
    "Next Usian Bolt here.",
    "Have to globally blacklist this guy for running so often ",
    "Yeah yeah, just tap /kickme and get over it.",
    "Run for ya life kid.. run for ya life, Chuck Norris is here.",
    "Legend has it, Temple Run was based on this guy...",
    "Calma ya not so mature horses, son..",
    "How about i cut ya legs out? Evil.. AhahaAh",
    "You are running like ya wife ran away with somebody else.",
    "Run and burn ya fat.",
    "Never come back again.",
    "You can't run without a brain - get one.",
    "NO RUNNING HERE ffs",
    "Mario is coming to hunt you down, baby.",
    "Who let the dogs out?",
    "It's so funny, because we don't care.",
    "Ah, what a waste.",
    "I don't give a damn.",
    "Run like it's the end of the world!",
    "You can't HANDLE the truth!",
    "Stop running else @mohancm100 or @kubersharma will gban you for life."
    "You can't run away from Thor's Hammer",
    "Prey is running",
    "Don't run away from me, i ain't grabbing ya, am i?",
    "KThnxBye",
)



@run_async
def runs(bot, update):
    update.effective_message.reply_text(random.choice(RUN_STRINGS))





@run_async
def get_bot_ip(bot, update):
    """ Sends the bot's IP address, so as to be able to ssh in if necessary.
        OWNER ONLY.
    """
    res = requests.get("http://ipinfo.io/ip")
    update.message.reply_text(res.text)


@run_async
def get_id(bot, update, args):
    user_id = extract_user(update.effective_message, args)
    if user_id:
        if update.effective_message.reply_to_message and update.effective_message.reply_to_message.forward_from:
            user1 = update.effective_message.reply_to_message.from_user
            user2 = update.effective_message.reply_to_message.forward_from
            update.effective_message.reply_text(
                "The original sender, {}, has an ID of `{}`.\nThe forwarder, {}, has an ID of `{}`.".format(
                    escape_markdown(user2.first_name),
                    user2.id,
                    escape_markdown(user1.first_name),
                    user1.id),
                parse_mode=ParseMode.MARKDOWN)
        else:
            user = bot.get_chat(user_id)
            update.effective_message.reply_text("{}'s id is `{}`.".format(escape_markdown(user.first_name), user.id),
                                                parse_mode=ParseMode.MARKDOWN)
    else:
        chat = update.effective_chat
        if chat.type == "private":
            update.effective_message.reply_text("Your id is `{}`.".format(chat.id),
                                                parse_mode=ParseMode.MARKDOWN)

        else:
            update.effective_message.reply_text("This group's id is `{}`.".format(chat.id),
                                                parse_mode=ParseMode.MARKDOWN)


@run_async
def info(bot, update, args):
    msg = update.effective_message
    user_id = extract_user(update.effective_message, args)
    if user_id:
        user = bot.get_chat(user_id)
    else:
        user = msg.from_user

    text = "Info" \
           "\nID: `{}`" \
           "\nFirst Name: {}".format(user.id, escape_markdown(user.first_name))

    if user.last_name:
        text += "\nLast Name: {}".format(escape_markdown(user.last_name))

    if user.username:
        text += "\nUsername: @{}".format(escape_markdown(user.username))

    if user.id == OWNER_ID:
        text += "\n\nThis person is my owner - I would never do anything against them!"
    else:
        if user.id in SUDO_USERS:
            text += "\nThis person is one of my sudo users! " \
                    "Nearly as powerful as my owner - so watch it."
        else:
            if user.id in SUPPORT_USERS:
                text += "\nThis person is one of my support users! " \
                        "Not quite a sudo user, but can still gban you off the map."

            if user.id in WHITELIST_USERS:
                text += "\nThis person has been whitelisted! " \
                        "That means I'm not allowed to ban/kick them."

    for mod in USER_INFO:
        mod_info = mod.__user_info__(user.id).strip()
        if mod_info:
            text += "\n\n" + mod_info

    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)



@run_async
def echo(bot, update):
    args = update.effective_message.text.split(None, 1)
    update.effective_message.reply_text(args[1], quote=False)
    update.effective_message.delete()


@run_async
def markdown_help(bot, update):
    update.effective_message.reply_text("""
Markdown is a very powerful formatting tool supported by telegram. {} has some enhancements, to make sure that \
saved messages are correctly parsed, and to allow you to create buttons.

- _italic_: wrapping text with '_' will produce italic text
- *bold*: wrapping text with '*' will produce bold text
- `code`: wrapping text with '`' will produce monospaced text, also known as 'code'
- [sometext](someURL): this will create a link - the message will just show 'sometext', and tapping on it will open\
 the page at 'someURL'.
EG: [test](example.com)
- [buttontext](buttonurl:someURL): this is a special enhancement to allow users to have telegram buttons in their\
 markdown. 'buttontext' will be what is displayed on the button, and 'someurl' will be the url which is opened
EG: [This is a button](buttonurl:example.com)

Note: this message has had markdown disabled, to allow you to see what the characters are.
""".format(bot.first_name))
    update.effective_message.reply_text("Try forwarding the following message to me, and you'll see!")
    update.effective_message.reply_text("/save test This is a markdown test. _italics_, *bold*, `code`, "
                                        "[URL](example.com) [button](buttonurl:github.com)")


@run_async
def stats(bot, update):
    update.effective_message.reply_text("\n".join([mod.__stats__() for mod in STATS]))


# /ip is for private use
__help__ = """
 - /id: get the current group id. If used by replying to a message, gets that user's id.
 - /runs: reply a random string from an array of replies.
 - /slap: slap a user, or get slapped if not a reply
 - /time <place>: gives the local time at the given place
 - /markdownhelp: quick summary of how markdown works in telegram - can only be called in private chats
 - /info: get information about a user
"""

__name__ = "Misc"

ID_HANDLER = CommandHandler("id", get_id, pass_args=True)
IP_HANDLER = CommandHandler("ip", get_bot_ip, filters=Filters.chat(OWNER_ID))

RUNS_HANDLER = CommandHandler("runs", runs)
INFO_HANDLER = CommandHandler("info", info, pass_args=True)

ECHO_HANDLER = CommandHandler("echo", echo, filters=CustomFilters.sudo_filter)
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help, filters=Filters.private)

STATS_HANDLER = CommandHandler("stats", stats, pass_args=True)

dispatcher.add_handler(ID_HANDLER)
dispatcher.add_handler(IP_HANDLER)
dispatcher.add_handler(RUNS_HANDLER)
dispatcher.add_handler(INFO_HANDLER)
dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)
dispatcher.add_handler(STATS_HANDLER)