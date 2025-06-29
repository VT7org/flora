import os
import re
import sys
from typing import List, Union

import yaml
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.types import Message

from WinxMusic.misc import SUDOERS
from WinxMusic.utils.database import get_lang, is_maintenance

languages = {}
commands = {}
helpers = {}
languages_present = {}

def load_yaml_file(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf8") as file:
        return yaml.safe_load(file)


def get_command(lang: str = "en") -> Union[str, List[str]]:
    if lang not in commands:
        lang = "en"
    return commands[lang]


def get_string(lang: str):
    if lang not in languages:
        lang = "en"
    return languages[lang]


def get_helpers(lang: str):
    if lang not in helpers:
        lang = "hi"
    return helpers[lang]


# Load English commands (main)
if not os.path.exists("./strings/cmds/en.yml"):
    print("Missing main command file: strings/cmds/en.yml")
    sys.exit(1)

commands["en"] = load_yaml_file("./strings/cmds/en.yml")
english_keys = set(commands["en"].keys())

# Load other command files
for filename in os.listdir("./strings/cmds/"):
    if filename.endswith(".yml") and filename != "en.yml":
        language_code = filename[:-4]
        commands[language_code] = load_yaml_file(os.path.join("./strings/cmds/", filename))

        # Check for missing keys
        missing_keys = english_keys - set(commands[language_code].keys())
        if missing_keys:
            print(f"Error: Missing keys in strings/cmds/{language_code}.yml: {', '.join(missing_keys)}")
            sys.exit(1)

# Load helper strings
for filename in os.listdir("./strings/helpers/"):
    if filename.endswith(".yml"):
        language_code = filename[:-4]
        helpers[language_code] = load_yaml_file(os.path.join("./strings/helpers/", filename))

# Load language files
if not os.path.exists("./strings/langs/en.yml"):
    print("Missing main language file: strings/langs/en.yml")
    print("Attempting fallback to hi.yml...")
    if not os.path.exists("./strings/langs/hi.yml"):
        print("Missing fallback language file: strings/langs/hi.yml")
        sys.exit(1)
    else:
        languages["hi"] = load_yaml_file("./strings/langs/hi.yml")
        languages_present["hi"] = languages["hi"].get("name", "Hindi")

languages["en"] = load_yaml_file("./strings/langs/en.yml")
languages_present["en"] = languages["en"].get("name", "English")

for filename in os.listdir("./strings/langs/"):
    if filename.endswith(".yml") and filename not in ("en.yml", "hi.yml"):
        language_name = filename[:-4]
        languages[language_name] = load_yaml_file(os.path.join("./strings/langs/", filename))

        # Ensure all English keys exist in each language file
        for item in languages["en"]:
            if item not in languages[language_name]:
                languages[language_name][item] = languages["en"][item]

        try:
            languages_present[language_name] = languages[language_name]["name"]
        except KeyError:
            print(
                f"There is an issue with strings/langs/{filename}. Missing 'name' key. "
                "Please fix or report it to @BillCore"
            )
            sys.exit(1)

if not commands:
    print("There's a problem loading the command files. Please report it to @TheTeamVivek.")
    sys.exit()


def command(
    commands: Union[str, List[str]],
    prefixes: Union[str, List[str], None] = "/",
    case_sensitive: bool = False,
):
    async def func(flt, client: Client, message: Message):
        lang_code = await get_lang(message.chat.id)
        try:
            _ = get_string(lang_code)
        except Exception:
            _ = get_string("en")

        if not await is_maintenance():
            if (message.from_user and message.from_user.id not in SUDOERS) or not message.from_user:
                if message.chat.type == ChatType.PRIVATE:
                    await message.reply_text(_["maint_4"])
                    return False
                return False

        if isinstance(commands, str):
            commands_list = [commands]
        else:
            commands_list = commands

        localized_commands = []
        en_commands = []

        for cmd in commands_list:
            localized_cmd = get_command(lang_code).get(cmd, "")
            if isinstance(localized_cmd, str):
                localized_commands.append(localized_cmd)
            elif isinstance(localized_cmd, list):
                localized_commands.extend(localized_cmd)

            en_cmd = get_command("en").get(cmd, "")
            if isinstance(en_cmd, str):
                en_commands.append(en_cmd)
            elif isinstance(en_cmd, list):
                en_commands.extend(en_cmd)

        username = client.me.username or ""
        text = message.text or message.caption
        message.command = None

        if not text:
            return False

        def match_command(cmd, text, with_prefix=True):
            if with_prefix and flt.prefixes:
                for prefix in flt.prefixes:
                    if text.startswith(prefix):
                        without_prefix = text[len(prefix):]
                        if re.match(
                            rf"^(?:{cmd}(?:@?{username})?)(?:\s|$)",
                            without_prefix,
                            flags=re.IGNORECASE if not flt.case_sensitive else 0,
                        ):
                            return prefix + cmd
            else:
                if re.match(
                    rf"^(?:{cmd}(?:@?{username})?)(?:\s|$)",
                    text,
                    flags=re.IGNORECASE if not flt.case_sensitive else 0,
                ):
                    return cmd
            return None

        all_commands = []

        if lang_code == "en":
            all_commands.extend((cmd, True) for cmd in en_commands)
        else:
            all_commands.extend((cmd, True) for cmd in en_commands)
            all_commands.extend((cmd, True) for cmd in localized_commands)
            all_commands.extend((cmd, False) for cmd in localized_commands)

        for cmd, with_prefix in all_commands:
            matched_cmd = match_command(cmd, text, with_prefix)
            if matched_cmd:
                without_command = re.sub(
                    rf"{matched_cmd}(?:@?{username})?\s?",
                    "",
                    text,
                    count=1,
                    flags=re.IGNORECASE if not flt.case_sensitive else 0,
                )
                message.command = [matched_cmd] + [
                    re.sub(r"\\([\"'])", r"\1", m.group(2) or m.group(3) or "")
                    for m in re.finditer(r'([^\s"\']+)|"([^"]*)"|\'([^\']*)\'', without_command)
                ]
                return True

        return False

    if prefixes == "" or prefixes is None:
        prefixes = set()
    else:
        prefixes = set(prefixes) if isinstance(prefixes, list) else {prefixes}

    return filters.create(
        func,
        "MultilingualCommandFilter",
        commands=commands,
        prefixes=prefixes,
        case_sensitive=case_sensitive,
        )
