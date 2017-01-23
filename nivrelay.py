import argparse
import asyncio
import configparser

from services.console_service import ConsoleService
from services.discord_service import DiscordService
from services.service_handler import ConfigType
from services.slack_service import SlackService
from services.xmpp_service import XMPPService

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Chat Relay",
        description="A script for relaying messages between different chat services."
    )
    parser.add_argument("-c", help="Config file location", default="config.ini")
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.c)

    for section_name in config.sections():
        section = config[section_name]

        sconf = dict()
        sconf["name"] = section_name
        sconf["receiver"] = section.get("receiver", "yes")
        sconf["broadcaster"] = section.get("broadcaster", "no")

        if not section.get("type", None):
            print("Section \"{}\" has no type!".format(section_name))
            continue
        else:
            sconf["type"] = section["type"]

        service = None
        if section["type"] == "Discord":
            service = DiscordService
        elif section["type"] == "Console":
            service = ConsoleService
        elif section["type"] == "XMPP":
            service = XMPPService
        elif section["type"] == "Slack":
            service = SlackService

        if service:
            for key, keytype in service.requested_config_values().items():
                if keytype is ConfigType.SINGLE_VALUE and key in section:
                    sconf[key] = section[key]
                elif keytype is ConfigType.MULTI_VALUE and key in section:
                    sconf[key] = section[key].strip().split("\n")
                else:
                    continue

            service = service(sconf)
            asyncio.ensure_future(service.start())

    asyncio.get_event_loop().run_forever()
