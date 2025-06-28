from datetime import datetime, timedelta
from re import findall
from re import sub as re_sub

from pyrogram import errors
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message

MARKDOWN = """
Read the text below carefully to understand how formatting works!

<u>Supported placeholders:</u>

{GROUPNAME} - Group name
{NAME} - User name
{ID} - User ID
{FIRSTNAME} - User's first name
{SURNAME} - User's surname if available, otherwise nothing
{USERNAME} - User's username

{TIME} - Current time
{DATE} - Current date
{WEEKDAY} - Current day of the week

<b><u>NOTE:</u></b> Placeholders only work in the welcome module.

<u>Supported formatting:</u>

<code>**Bold**</code>: This will appear as <b>Bold</b> text.
<code>~~strikethrough~~</code>: This will appear as <strike>strikethrough</strike> text.
<code>__italic__</code>: This will appear as <i>italic</i> text.
<code>--underline--</code>: This will appear as <u>underline</u> text.
<code>`code words`</code>: This will appear as <code>code</code> text.
<code>||spoiler||</code>: This will appear as <spoiler>Spoiler</spoiler> text.
<code>[hyperlink](google.com)</code>: This will create a <a href='https://www.google.com'>hyperlink</a>.
<code>> hello</code>: This will appear as <blockquote>hello</blockquote>.
<b>Note:</b> You can use both Markdown and HTML tags.

<u>Button formatting:</u>

- > <blockquote>text ~ [button text, button link]</blockquote>

<u>Example:</u>

<b>Example</b>  
<blockquote><i>button with markdown</i> <code>formatting</code> ~ [button text, https://google.com]</blockquote>
"""
WELCOMEHELP = """
/setwelcome - Reply to this message with the correct format for a welcome message, check the end of this message.

/delwelcome - Deletes the welcome message.
/getwelcome - Displays the welcome message.

<b>SET_WELCOME -></b>

<b>To set a photo or GIF as a welcome message, add your welcome message as the caption of the photo or GIF. The caption must follow the format below.</b>

For a text welcome message, simply send the text. Then reply with the command.

The format should be something like this:

{GROUPNAME} - Group name
{NAME} - User's first name + surname
{ID} - User ID
{FIRSTNAME} - User's first name
{SURNAME} - User's surname if available, otherwise nothing
{USERNAME} - User's username

{TIME} - Current time
{DATE} - Current date
{WEEKDAY} - Current day of the week

~ #This separator (~) must be between the text and buttons, remove this comment as well.

button=[Duck, https://duckduckgo.com]
button2=[Github, https://github.com]

<b>NOTES -></b>

Check /markdownhelp for more information on formatting and other syntax.
"""


def get_urls_from_text(text: str) -> bool:
    regex = r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]
                [.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(
                \([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\
                ()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""".strip()
    return [x[0] for x in findall(regex, str(text))]


def extract_text_and_keyb(ikb, text: str, row_width: int = 2):
    keyboard = {}
    try:
        text = text.strip()
        if text.startswith("`"):
            text = text[1:]
        if text.endswith("`"):
            text = text[:-1]

        if "~~" in text:
            text = text.replace("~~", "¤¤")
        text, keyb = text.split("~")
        if "¤¤" in text:
            text = text.replace("¤¤", "~~")

        keyb = findall(r"\[.+\,.+\]", keyb)
        for btn_str in keyb:
            btn_str = re_sub(r"[\[\]]", "", btn_str)
            btn_str = btn_str.split(",")
            btn_txt, btn_url = btn_str[0], btn_str[1].strip()

            if not get_urls_from_text(btn_url):
                continue
            keyboard[btn_txt] = btn_url
        keyboard = ikb(keyboard, row_width)
    except Exception:
        return
    return text, keyboard


async def check_format(ikb, raw_text: str):
    keyb = findall(r"\[.+\,.+\]", raw_text)
    if keyb and not "~" in raw_text:
        raw_text = raw_text.replace("button=", "\n~\nbutton=")
        return raw_text
    if "~" in raw_text and keyb:
        if not extract_text_and_keyb(ikb, raw_text):
            return ""
        else:
            return raw_text
    else:
        return raw_text


async def get_data_and_name(replied_message, message):
    text = message.text.markdown if message.text else message.caption.markdown
    name = text.split(None, 1)[1].strip()
    text = name.split(" ", 1)
    if len(text) > 1:
        name = text[0]
        data = text[1].strip()
        if replied_message and (replied_message.sticker or replied_message.video_note):
            data = None
    else:
        if replied_message and (replied_message.sticker or replied_message.video_note):
            data = None
        elif (
                replied_message and not replied_message.text and not replied_message.caption
        ):
            data = None
        else:
            data = (
                replied_message.text.markdown
                if replied_message.text
                else replied_message.caption.markdown
            )
            command = message.command[0]
            match = f"/{command} " + name
            if not message.reply_to_message and message.text:
                if match == data:
                    data = "error"
            elif not message.reply_to_message and not message.text:
                if match == data:
                    data = None
    return data, name


async def extract_userid(message, text: str):
    """
    NOT TO BE USED OUTSIDE THIS FILE
    """

    def is_int(text: str):
        try:
            int(text)
        except ValueError:
            return False
        return True

    text = text.strip()

    if is_int(text):
        return int(text)

    entities = message.entities
    app = message._client
    if len(entities) < 2:
        return (await app.get_users(text)).id
    entity = entities[1]
    if entity.type == MessageEntityType.MENTION:
        return (await app.get_users(text)).id
    if entity.type == MessageEntityType.TEXT_MENTION:
        return entity.user.id
    return None


async def extract_user_and_reason(message, sender_chat=False):
    args = message.text.strip().split()
    text = message.text
    user = None
    reason = None

    try:
        if message.reply_to_message:
            reply = message.reply_to_message
            if not reply.from_user:
                if (
                        reply.sender_chat
                        and reply.sender_chat != message.chat.id
                        and sender_chat
                ):
                    id_ = reply.sender_chat.id
                else:
                    return None, None
            else:
                id_ = reply.from_user.id

            if len(args) < 2:
                reason = None
            else:
                reason = text.split(None, 1)[1]
            return id_, reason

        # if not reply to a message and no reason is given
        if len(args) == 2:
            user = text.split(None, 1)[1]
            return await extract_userid(message, user), None

        # if reason is given
        if len(args) > 2 --snip--
        if len(args) > 2:
            user, reason = text.split(None, 2)[1:]
            return await extract_userid(message, user), reason

        return user, reason

    except errors.UsernameInvalid:
        return "", ""


async def extract_user(message):
    return (await extract_user_and_reason(message))[0]


def get_file_id_from Gettable(
        message,
        max_file_size=3145728,
        mime_types=["image/png", "image/jpeg"],
):
    file_id = None
    if message.document:
        if int(message.document.file_size) > max_file_size:
            return

        mime_type = message.document.mime_type

        if mime_types and mime_type not in mime_types:
            return
        file_id = message.document.file_id

    if message.sticker:
        if message.sticker.is_animated:
            if not message.sticker.thumbs:
                return
            file_id = message.sticker.thumbs[0].file_id
        else:
            file_id = message.sticker.file_id

    if message.photo:
        file_id = message.photo.file_id

    if message.animation:
        if not message.animation.thumbs:
            return
        file_id = message.animation.thumbs[0].file_id

    if message.video:
        if not message.video.thumbs:
            return
        file_id = message.video.thumbs[0].file_id
    return file_id


async def time_converter(message: Message, time_value: str) -> Message | datetime:
    unit = ["m", "h", "d"]
    check_unit = "".join(list(filter(time_value[-1].lower().endswith, unit)))
    currunt_time = datetime.now()
    time_digit = time_value[:-1]
    if not time_digit.isdigit():
        return await message.reply_text("Incorrect time specified.")
    if check_unit == "m":
        temp_time = currunt_time + timedelta(minutes=int(time_digit))
    elif check_unit == "h":
        temp_time = currunt_time + timedelta(hours=int(time_digit))
    elif check_unit == "d":
        temp_time = currunt_time + timedelta(days=int(time_digit))
    else:
        return await message.reply_text("Incorrect time specified.")
    return temp_time
